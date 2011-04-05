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


class HasFileForm(forms.ModelForm):

    def save(self, commit=True):
        m = super(HasFileForm, self).save(commit=False)
        file_field = self.cleaned_data['file']
        if file_field:
            m.file_md5 = get_file_md5(file_field.file)
        if commit:
            m.save()
        return m


class HasFileInline(admin.StackedInline):
    form = HasFileForm
    extra = 1
    list_display = ('titel', 'file')
    ordering = ('titel',)
    exclude = ('file_md5',)


class BilagaInline(HasFileInline):
    model = Bilaga


class OvrigtDokumentInline(HasFileInline):
    model = OvrigtDokument


class MyndighetsforeskriftAdmin(admin.ModelAdmin):
    list_display = ('identifierare', 'arsutgava', 'lopnummer', 'titel','beslutsdatum', 'ikrafttradandedatum', 'utkom_fran_tryck', 'typ')
    list_filter = ('beslutsdatum', 'ikrafttradandedatum')
    ordering = ('-beslutsdatum', 'titel')
    search_fields = ('titel', 'identifierare',)
    inlines = [BilagaInline, OvrigtDokumentInline]

    def save_model(self, request, obj, form, change):
        """Se till att AtomEntry-objekt skaps i samband med att
        myndighetsföreskrifter sparas och uppdateras. Se även
        create_delete_entry i rinfo/models.py för detaljer om det entry som
        skapas när en post raderas."""

        # Först, spara ner föreskriften och relationer till andra objekt
        super(MyndighetsforeskriftAdmin, self).save_model(request, obj, form, change)
        form.save_m2m()
        obj.save()

        # Nu kan vi skapa ett AtomEntry

        # Då posten publicerades (nu, om det är en ny post)
        published = datetime.now()

        # Se om det finns ett tidigare AtomEntry för denna föreskrift.
        try:
            foreskrift_entries = AtomEntry.objects.filter(foreskrift=obj.id).order_by("published")
            if foreskrift_entries:
                published = foreskrift_entries[0].published
        except AtomEntry.DoesNotExist:
            # Kan inte hitta AtomEntry för denna föreskrift. Därmed är det en ny post.
            pass

        # Beräkna md5 för dokumentet
        with open(obj.dokument.path, 'rb') as f:
            dokument_md5 = get_file_md5(f)

        # ...och för metadataposten i RDF-format
        md5 = hashlib.md5()
        rdfxml_repr = obj.to_rdfxml().encode("utf-8")
        md5.update(rdfxml_repr)
        rdf_md5 = md5.hexdigest()

        # Skapa AtomEntry-posten
        entry = AtomEntry(  foreskrift=obj,
                title=obj.titel,
                summary=obj.sammanfattning,
                updated=datetime.now(),
                published=published,
                entry_id=obj.get_rinfo_uri(),
                content_md5=dokument_md5,
                content_src=obj.dokument.url,
                rdf_href=obj.get_absolute_url() + "rdf",
                rdf_length=len(rdfxml_repr),
                rdf_md5=rdf_md5)

        # Spara AtomEntry för denna aktivitet
        entry.save()


# Registrera adminklasserna
admin.site.register(Amnesord, AmnesordAdmin)
admin.site.register(CelexReferens, CelexReferensAdmin)
admin.site.register(Forfattningssamling, ForfattningssamlingAdmin)
admin.site.register(Myndighetsforeskrift, MyndighetsforeskriftAdmin)
admin.site.register(Bemyndigandereferens)
admin.site.register(AtomEntry)


