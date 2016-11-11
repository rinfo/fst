# -*- coding: utf-8 -*-
"""Layout and behavior of fs_doc admin app"""

from os import path
from datetime import datetime
from itertools import chain
from operator import attrgetter
import re
from django.db import models
from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.core.files import File
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import  loader, Context, RequestContext
from django.contrib import admin
from fst_web.adminplus.sites import AdminSitePlus
from fst_web.fs_doc.models import *


# Add admin enhancements from AdminPlus
admin.site = AdminSitePlus()

LIST_PER_PAGE_COUNT = 25 # Number of documents before automatic pagination

class ForfattningssamlingAdmin(admin.ModelAdmin):
    list_display = ('titel', 'kortnamn', 'identifierare')
    ordering = ('titel',)
    fieldsets = ((None, {
        'fields': (
            'titel',
            'kortnamn')}),)

    def save_model(self, request, obj, form, change):
        obj.slug = to_slug(obj.kortnamn)
        obj.save
        super(ForfattningssamlingAdmin, self).save_model(
            request, obj, form, change)


class CelexReferensAdmin(admin.ModelAdmin):
    list_display = ('celexnummer', 'titel')
    ordering = ('celexnummer',)
    search_fields = ('celexnummer', 'titel')


class AmnesordAdmin(admin.ModelAdmin):
    list_display = ('titel', 'beskrivning')
    ordering = ('titel',)
    search_fields = ('titel', 'beskrivning',)


class BemyndigandereferensAdmin(admin.ModelAdmin):
    list_display = ('sfsnummer', 'titel', 'kapitelnummer', 'paragrafnummer')
    ordering = ('titel',)
    search_fields = ('titel', 'sfsnummer',)


class HasFileForm(forms.ModelForm):

    FILE_FIELD_KEY = 'file'

    def save(self, commit=True):
        m = super(HasFileForm, self).save(commit=False)
        file_field = self.cleaned_data[self.FILE_FIELD_KEY]
        file_md5_key = '%s_md5' % self.FILE_FIELD_KEY
        if file_field:
            setattr(m, file_md5_key, get_file_md5(file_field.file))
        if commit:
            m.save()
        return m


class HasFileInline(admin.TabularInline):
    form = HasFileForm
    extra = 1
    list_display = ('titel', 'file')
    ordering = ('titel',)
    exclude = ('file_md5',)


class BilagaInline(HasFileInline):
    model = Bilaga
    classes = ['collapse', 'collapsed']


class OvrigtDokumentInline(HasFileInline):
    model = OvrigtDokument
    classes = ['collapse', 'collapsed']


class HasContentFileForm(HasFileForm):

    FILE_FIELD_KEY = 'content'


class FSDokumentAdminMixin(object):


    view_on_site = False  # Hide link to raw metadata

    def save_model(self, request, obj, form, change):
        """Create an AtomEntry object when 'Myndighetsforeskrift' is saved or
        updated. See 'create_delete_entry' in 'rinfo/models.py' for
        deletion."""

        # Save the document and it's relations to other objects
        super(FSDokumentAdminMixin, self).save_model(
            request, obj, form, change)
        form.save_m2m()
        obj.save()
        # Now save RDF representation and Atom post
        generate_rdf_post_for(obj)
        generate_atom_entry_for(obj, update_only=True)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "forfattningssamling":
            kwargs["initial"] = Forfattningssamling.objects.filter(id=1)
        return super(
            FSDokumentAdminMixin, self).formfield_for_foreignkey(
                db_field, request, **kwargs)

    def make_published(self, request, queryset):
        """Puslish selected documents by creating Atom entries."""

        for i, obj in enumerate(queryset):
            generate_atom_entry_for(obj)
            obj.is_published = True
            obj.save()
            self.message_user(
                request, "%s dokument har publicerats." % (i + 1))

    make_published.short_description = u"Publicera markerade dokument via FST"
    actions = [make_published]

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        """Get a form Field for a ManyToManyField """

        if db_field.name in ["andringar", "upphavningar"]:
            kwargs['widget'] = admin.widgets.FilteredSelectMultiple(
                      "dokument", (db_field.name in self.filter_vertical))
        elif db_field.name == "celexreferenser":
            kwargs['widget'] = \
            admin.widgets.FilteredSelectMultiple(
                u"celex-referenser", (db_field.name in self.filter_vertical))
        else:
            kwargs['widget'] = admin.widgets.FilteredSelectMultiple(
                db_field.verbose_name, (db_field.name in self.filter_vertical))
        return db_field.formfield(**kwargs)


class AllmannaRadAdmin(FSDokumentAdminMixin, admin.ModelAdmin):

    form = HasContentFileForm

    list_display = ('identifierare',
                    'arsutgava',
                    'lopnummer',
                    'titel',
                    'beslutsdatum',
                    'ikrafttradandedatum',
                    'utkom_fran_tryck',
                    'role_label')
    list_filter = ('beslutsdatum',
                   'ikrafttradandedatum',
                   'is_published',
                   'amnesord',
                   #'andrar',
                   'omtryck')
    ordering = ('-beslutsdatum', 'titel')
    search_fields = ('titel', 'arsutgava', 'lopnummer')
    inlines = [BilagaInline, OvrigtDokumentInline]
    readonly_fields = ('is_published', 'identifierare',)
    save_on_top = True
    list_per_page = LIST_PER_PAGE_COUNT
    fieldsets = (
        (None,
         {
             'fields': (
                 'is_published',
                 'identifierare',
                 'forfattningssamling',
                 ('arsutgava', 'lopnummer'),
                 ('content', 'omtryck'),
                 ('titel', 'sammanfattning'),
                 ('beslutsdatum', 'utkom_fran_tryck', 'ikrafttradandedatum'),
                 ),
             'classes': ['wide', 'extrapretty']}
         ),
        (u'Dokument som detta dokument ändrar',
         {
             'fields': ('andringar',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'Dokument som detta dokument upphäver',
         {
             'fields': ('upphavningar',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'Ämnesord - myndighetens kategorisering',
         {
             'fields': (
                 'amnesord',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         )
    )
    filter_horizontal = ('amnesord',
                         'andringar',
                         'upphavningar',
                         'konsolideringar')

    def formfield_for_dbfield(self, db_field, **kwargs):
        """"Use different or modified widgets for some fields """

        if isinstance(db_field, models.CharField):
            if db_field.name == "titel":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 100, 'rows': 2, 'class': 'docx'})
            if db_field.name == "arsutgava" or db_field.name == "lopnummer":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 10, 'rows': 1})
        if isinstance(db_field, models.TextField):
            if db_field.name == "sammanfattning":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 100, 'rows': 5, 'class': 'docx'})
        return super(AllmannaRadAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)


class MyndighetsforeskriftAdmin(FSDokumentAdminMixin, admin.ModelAdmin):

    form = HasContentFileForm

    list_display = ('identifierare',
                    'arsutgava',
                    'lopnummer',
                    'titel',
                    'beslutsdatum',
                    'ikrafttradandedatum',
                    'utkom_fran_tryck',
                    'role_label')
    list_filter = ('beslutsdatum',
                   'ikrafttradandedatum',
                   'is_published',
                   'amnesord',
                   #'andrar',
                   'omtryck')
    ordering = ('-beslutsdatum', 'titel')
    search_fields = ('titel',  'arsutgava', 'lopnummer')
    inlines = [BilagaInline, OvrigtDokumentInline]
    readonly_fields = ('is_published', 'identifierare',)
    save_on_top = True
    list_per_page = LIST_PER_PAGE_COUNT
    fieldsets = (
        (None,
         {
             'fields': (
                 'is_published',
                 'identifierare',
                 'forfattningssamling',
                 ('arsutgava', 'lopnummer'),
                 ('content', 'omtryck'),
                 ('titel', 'sammanfattning'),
                 ('beslutsdatum', 'utkom_fran_tryck', 'ikrafttradandedatum'),
                 ('utgivare', 'beslutad_av'),
                 'bemyndiganden'
                 ),
             'classes': ['wide', 'extrapretty']
             }),
        (u'Dokument som detta dokument ändrar',
         {
             'fields': ('andringar',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'Dokument som detta dokument upphäver',
         {
             'fields': ('upphavningar',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'EU-rättsreferenser',
         {
             'fields': (
                 'celexreferenser',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'Ämnesord - myndighetens kategorisering',
         {
             'fields': (
                 'amnesord',),
             'classes': ['collapse', 'wide', 'extrapretty']}
         )
    )
    filter_horizontal = ('bemyndiganden',
                         'amnesord',
                         'andringar',
                         'upphavningar',
                         'konsolideringar',
                         'celexreferenser')

    def formfield_for_dbfield(self, db_field, **kwargs):
        """"Use different or modified widgets for some fields """

        if isinstance(db_field, models.CharField):
            if db_field.name == "titel":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 100, 'rows': 2, 'class': 'docx'})
            if db_field.name == "arsutgava" or db_field.name == "lopnummer":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 10, 'rows': 1})
        if isinstance(db_field, models.TextField):
            if db_field.name == "sammanfattning":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 100, 'rows': 5, 'class': 'docx'})
        return super(MyndighetsforeskriftAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)
    

class KonsolideradForeskriftAdmin(FSDokumentAdminMixin, admin.ModelAdmin):

    form = HasContentFileForm

    model = KonsolideradForeskrift
    list_display = ('identifierare',
                    'titel',
                    'konsolideringsdatum')
    save_on_top = True
    list_per_page = LIST_PER_PAGE_COUNT
    exclude = ('content_md5',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        """"Use different or modified widgets for some fields """

        if isinstance(db_field, models.CharField):
            if db_field.name == "titel":
                kwargs['widget'] = forms.Textarea(
                    attrs={'cols': 100, 'rows': 2, 'class': 'docx'})
        return super(KonsolideradForeskriftAdmin, self).formfield_for_dbfield(
            db_field, **kwargs)


def _response(request, template, context):
    return render_to_response(template,
                              context)


def amnesord(request):
    """Display documents grouped by keywords """

    def get_identifierare(obj):
        return obj.identifierare

    # Get all keywords used by at least one document
    amnesord = list(
        Amnesord.objects.filter(fsdokument__isnull = False).
        order_by("titel").distinct())

    # Create a dictionary on keywords for all types of documents
    docs_by_keywords = {}
    for kw in (amnesord):
        doc_list = list(kw.fsdokument_set.all())
        doc_list.sort(key=get_identifierare)
        docs_by_keywords[kw] = doc_list
    return _response(request, 'per_amnesord.html', locals())


def arsutgava(request):
    """Display documents grouped by year """

    def get_key(obj):
        for num, rest, in re.findall(r'(\d+)(.*)',
                                                     obj.lopnummer):
            num = int(num)
            break
        else:
            num, rest= lopnummer, ''
        return (obj.arsutgava, num)

    f_list = list(Myndighetsforeskrift.objects.all())
    a_list = list(AllmannaRad.objects.all())
    fs_documents = list(chain(f_list, a_list))
    fs_documents.sort(key=get_key,reverse = True)
    return _response(request, 'per_identifierare.html', locals())

def ikrafttradande(request):
    """Display documents grouped by year """
        
    def get_ikrafttradandedatum(obj):
        return obj.ikrafttradandedatum
    
    f_list = list(Myndighetsforeskrift.objects.all())
    a_list = list(AllmannaRad.objects.all())
    fs_documents = list(chain(f_list, a_list))
    fs_documents.sort(key=get_ikrafttradandedatum,reverse = True)
    return _response(request, 'per_ar.html', locals())


def beslutsdatum(request):
    """Display start page

    List the latest documents in current document collection.
    Get both 'Myndighetsforeskrift' and 'AllmannaRad'.
    """

    f_list = list(Myndighetsforeskrift.objects.all().order_by(
        "-beslutsdatum"))
    a_list = list(AllmannaRad.objects.all().order_by(
        "-beslutsdatum"))
    all_docs = sorted(
        chain(f_list, a_list),
        key=attrgetter('beslutsdatum'),
        reverse=True)
    latest_documents = all_docs[:LIST_PER_PAGE_COUNT]
    return _response(request, 'beslutsdatum.html', locals())

def not_published(request):
    """Display start page

    List all documents that are not published
    Get both 'Myndighetsforeskrift' and 'AllmannaRad'.
    """
    f_list = list(Myndighetsforeskrift.objects.all().filter(is_published=False).order_by(
        "-beslutsdatum"))
    a_list = list(AllmannaRad.objects.all().filter(is_published=False) .order_by(
        "-beslutsdatum"))
    all_docs = sorted(
        chain(f_list, a_list),
        key=attrgetter('beslutsdatum'),
        reverse=True)
    latest_documents = all_docs[:LIST_PER_PAGE_COUNT]
    return _response(request, 'not_published.html', locals())


admin.site.register_view(
    'beslutsdatum',
    u'Senast publicerade (per beslutsdatum)',
    view=beslutsdatum)


admin.site.register_view(
    'ikrafttradande', 
    u'Senast publicerade (per år för ikraftträdande)',
    view=ikrafttradande)


admin.site.register_view(
    'not_published',
    u'Ej publicerade dokument',
    view=not_published)


# TODO - Fix this view so get_admin_url doesn't get called with FSDokument
# instead of Myndighetsforeskrift or AllmannaRad
#admin.site.register_view(
#    'amnesord', amnesord,
#    u'Lista föreskrifter och allmänna råd (per ämnesord)')

admin.site.register(AllmannaRad, AllmannaRadAdmin)
admin.site.register(Myndighetsforeskrift, MyndighetsforeskriftAdmin)
admin.site.register(Amnesord, AmnesordAdmin)
admin.site.register(Bemyndigandereferens, BemyndigandereferensAdmin)
admin.site.register(CelexReferens, CelexReferensAdmin)
admin.site.register(Forfattningssamling, ForfattningssamlingAdmin)
admin.site.register(KonsolideradForeskrift, KonsolideradForeskriftAdmin)
admin.site.register(AtomEntry)
admin.site.register(Myndighet)


# Adminplus fails to add these, so we must do it ourselves
from django.contrib.auth.admin import User, Group, UserAdmin
#from django.contrib.sites.admin import Site

admin.site.register(Group)
#admin.site.register(Site)
admin.site.register(User, UserAdmin)