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
        obj.slug = obj.get_slug(obj.kortnamn)
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
    list_display = ('sfsnummer','titel','kapitelnummer','paragrafnummer')
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


class AllmannaRadAdmin(admin.ModelAdmin):
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
                   'publicerad',
                   'amnesord',
                   #'andrar',
                   'omtryck')
    ordering = ('-beslutsdatum', 'titel')
    search_fields = ('titel', 'identifierare',)
    #inlines = [BilagaInline, OvrigtDokumentInline]
    readonly_fields = ('publicerad','identifierare',)
    save_on_top = True
    fieldsets = ((None, {
        'fields': (
            'identifierare',
            'publicerad',
            'forfattningssamling',
            ('arsutgava', 'lopnummer'),
            'titel',
            'sammanfattning',
            'content',
            ('beslutsdatum', 'ikrafttradandedatum', 'utkom_fran_tryck'),
            'omtryck',
            #('omtryck','andrar'),
            #'bemyndiganden',
            'amnesord',
            #'celexreferenser'
            ),
        'classes': ['wide', 'extrapretty']
        }),)
    filter_horizontal = ('amnesord',)


class MyndighetsforeskriftAdmin(admin.ModelAdmin):

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
                   'publicerad',
                   'amnesord',
                   'andrar',
                   'omtryck')
    ordering = ('-beslutsdatum', 'titel')
    search_fields = ('titel', 'identifierare',)
    inlines = [BilagaInline, OvrigtDokumentInline]
    readonly_fields = ('publicerad','identifierare',)
    save_on_top = True
    fieldsets = ((None, {
        'fields': (
            'identifierare',
            'publicerad',
            'forfattningssamling',
            ('arsutgava', 'lopnummer'),
            'titel',
            'sammanfattning',
            'content',
            ('beslutsdatum', 'ikrafttradandedatum', 'utkom_fran_tryck'),
            ('omtryck','andrar'),
            'bemyndiganden',
            'amnesord',
            'celexreferenser'
            ),
        'classes': ['wide', 'extrapretty']
        }),)
    filter_horizontal = ('bemyndiganden','amnesord','celexreferenser')

    def save_model(self, request, obj, form, change):
        """Create an AtomEntry object when 'Myndighetsforeskrift' is saved or updated. See 'create_delete_entry' in 'rinfo/models.py' for deletion."""

        # Save the document and it's relations to other objects
        super(MyndighetsforeskriftAdmin, self).save_model(
            request, obj, form, change)
        form.save_m2m()
        obj.save()
        # Then create new entry
        self._create_entry(obj)

    def _create_entry(self, obj):
        updated = datetime.now()

        # Check if we already published this document
        obj_type = ContentType.objects.get_for_model(obj)
        entries = AtomEntry.objects.filter(content_type__pk=obj_type.id,
                                           object_id=obj.id)
        for entry in entries.order_by("published"):
            published = entry.published
            break
        else:
            # For new documents
            published = updated

        # Create RDF metadata
        rdf_post = RDFPost.create_for(obj)
        rdf_post.save()

        entry = AtomEntry(content_object=obj,
                          entry_id=obj.get_rinfo_uri(),
                          updated=updated, published=published,
                          rdf_post=rdf_post)
        entry.save()


    #TODO: replace setting of field 'published' with complete atom feed workflow
    def make_published(self, request, queryset):
        rows_updated = queryset.update(publicerad=True)
        if rows_updated == 1:
            message_bit = "1 föreskrift"
        else:
            message_bit = "%s föreskrifter" % rows_updated
        self.message_user(request, "%s har publicerats." % message_bit)

    make_published.short_description = u"Publicera markerade \
                  föreskrifter via FST"
    actions = [make_published]


admin.site.register(AllmannaRad, AllmannaRadAdmin)
admin.site.register(Myndighetsforeskrift, MyndighetsforeskriftAdmin)
admin.site.register(Amnesord, AmnesordAdmin)
admin.site.register(Bemyndigandereferens,BemyndigandereferensAdmin)
admin.site.register(CelexReferens, CelexReferensAdmin)
admin.site.register(Forfattningssamling, ForfattningssamlingAdmin)
admin.site.register(AtomEntry)
admin.site.register(Myndighet)

