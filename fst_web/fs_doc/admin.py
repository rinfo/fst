# -*- coding: utf-8 -*-
from os import path
from datetime import datetime
from django import forms
from django.contrib import admin
from django.core.files import File
from django.conf import settings
from fst_web.fs_doc.models import *


class ForfattningssamlingAdmin(admin.ModelAdmin):
    list_display = ('titel', 'kortnamn', 'identifierare')
    ordering = ('titel',)
    fieldsets = ((None, {
        'fields': (
            'titel',
            'kortnamn')}),)

    def save_model(self, request, obj, form, change):
        obj.slug = to_slug(obj.kortnamn)
        super(ForfattningssamlingAdmin, self).save_model(
            request, obj, form, change)
        obj.save


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


class AllmannaRadAdmin(FSDokumentAdminMixin, admin.ModelAdmin):
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
    search_fields = ('titel', 'identifierare',)
    #inlines = [BilagaInline, OvrigtDokumentInline]
    readonly_fields = ('is_published', 'identifierare',)
    save_on_top = True
    fieldsets = (
        (None,
         {
             'fields': (
                 'is_published',
                 'identifierare',
                 ('forfattningssamling', 'arsutgava', 'lopnummer'),
                 ('titel', 'sammanfattning'),
                 ('content', 'omtryck'),
                 ('beslutsdatum', 'ikrafttradandedatum', 'utkom_fran_tryck'),
                 ),
             'classes': ['wide', 'extrapretty']
             }),
        (u'Dokument som ändras, upphävs eller konsolideras av detta dokument',
         {
             'fields': ('andringar','upphavningar'),
             'description': u'Ange eventuella andra dokument påverkas',
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'Ämnesord (myndighetens kategorisering)',
         {
             'fields': (
                 'amnesord',),
             'classes': ['collapse', 'wide', 'extrapretty']
         })
    )
    filter_horizontal = ('amnesord', 'andringar', 'upphavningar')


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
    search_fields = ('titel', 'identifierare',)
    inlines = [BilagaInline, OvrigtDokumentInline]
    readonly_fields = ('is_published', 'identifierare',)
    save_on_top = True
    fieldsets = (
        (None,
         {
             'fields': (
                 'is_published',
                 'identifierare',
                 ('forfattningssamling', 'arsutgava', 'lopnummer'),
                 ('titel', 'sammanfattning'),
                 ('content', 'omtryck'),
                 ('beslutsdatum', 'ikrafttradandedatum', 'utkom_fran_tryck'),
                 'bemyndiganden',
                 'celexreferenser'
                 ),
             'classes': ['wide', 'extrapretty']
             }),
        (u'Författningsdokument som ändras, upphävs eller konsolideras',
         {
             'fields': ('andringar', 'upphavningar'),
             'description': u'Ange eventuella andra dokument påverkas',
             'classes': ['collapse', 'wide', 'extrapretty']}
         ),
        (u'Ämnesord (myndighetens kategorisering)',
         {
             'fields': (
                 'amnesord',),
             'classes': ['collapse', 'wide', 'extrapretty']
         })
    )
    filter_horizontal = ('bemyndiganden', 'amnesord', 'andringar', 'upphavningar','celexreferenser')


def generate_atom_entry_for(obj, update_only=False):
    updated = datetime.now()

    # Check if we already published this document
    obj_type = ContentType.objects.get_for_model(obj)
    entries = AtomEntry.objects.filter(content_type__pk=obj_type.id,
                                       object_id=obj.id)
    # Find entry for object
    for entry in entries.order_by("published"):
        entry_published = entry.published
        break
    else:
        if update_only:
            return
        # For new documents
        entry_published = updated

    # Get RDF representation of object
    rdf_post = RDFPost.get_for(obj)

    entry = AtomEntry.get_or_create(obj)
    entry.entry_id = obj.get_rinfo_uri()
    entry.updated = updated
    entry.published = entry_published
    entry.rdf_post = rdf_post
    entry.save()


def generate_rdf_post_for(obj):
    # Create RDF metadata
    rdf_post = RDFPost.get_or_create(obj)
    rdf_post.slug = obj.get_fs_dokument_slug()
    rdf_post.data = obj.to_rdfxml()
    rdf_post.save()
    return rdf_post


admin.site.register(AllmannaRad, AllmannaRadAdmin)
admin.site.register(Myndighetsforeskrift, MyndighetsforeskriftAdmin)
admin.site.register(Amnesord, AmnesordAdmin)
admin.site.register(Bemyndigandereferens, BemyndigandereferensAdmin)
admin.site.register(CelexReferens, CelexReferensAdmin)
admin.site.register(Forfattningssamling, ForfattningssamlingAdmin)
admin.site.register(AtomEntry)
admin.site.register(Myndighet)
