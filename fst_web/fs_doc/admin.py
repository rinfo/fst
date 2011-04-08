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


class MyndighetsforeskriftAdmin(admin.ModelAdmin):

    form = HasContentFileForm

    list_display = ('identifierare', 'arsutgava', 'lopnummer', 'titel','beslutsdatum', 'ikrafttradandedatum', 'utkom_fran_tryck', 'typ')
    list_filter = ('beslutsdatum', 'ikrafttradandedatum','publicerad','amnesord','andrar','omtryck')
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
        """Se till att AtomEntry-objekt skaps i samband med att
        myndighetsföreskrifter sparas och uppdateras. Se även
        create_delete_entry i rinfo/models.py för detaljer om det entry som
        skapas när en post raderas."""

        # Först, spara ner föreskriften och relationer till andra objekt
        super(MyndighetsforeskriftAdmin, self).save_model(
                request, obj, form, change)
        form.save_m2m()
        obj.save()
        self._create_entry(obj)

    def _create_entry(self, obj):
        # Då posten publicerades (nu, om det är en ny post)
        updated = datetime.now()

        # Se om det finns ett tidigare AtomEntry för denna föreskrift
        try:
            for entry in AtomEntry.objects.filter(foreskrift=obj.id) \
                    .order_by("published"):
                published = entry.published
                break
        except AtomEntry.DoesNotExist:
            # Om inte är den ny
            published = updated

        # Skapa metadatapost i RDF-format
        rdf_post = RDFPost.create_for(obj)
        rdf_post.save()

        entry = AtomEntry(foreskrift=obj,
                entry_id=obj.get_rinfo_uri(),
                updated=updated, published=published,
                rdf_post=rdf_post)
        entry.save()

    def make_published(self, request, queryset):
        rows_updated = queryset.update(publicerad=True)
        if rows_updated == 1:
            message_bit = "1 föreskrift"
        else:
            message_bit = "%s föreskrifter" % rows_updated
        self.message_user(request, "%s har publicerats." % message_bit)

    make_published.short_description = u"Publicera markerade föreskrifter via FST"
    actions = [make_published]


# Registrera adminklasserna
admin.site.register(Amnesord, AmnesordAdmin)
admin.site.register(CelexReferens, CelexReferensAdmin)
admin.site.register(Forfattningssamling, ForfattningssamlingAdmin)
admin.site.register(Myndighetsforeskrift, MyndighetsforeskriftAdmin)
admin.site.register(Bemyndigandereferens,BemyndigandereferensAdmin)
admin.site.register(AtomEntry)



