# coding=utf-8
from django.contrib import admin
from rinfo.models import *
import hashlib
from datetime import datetime
from django.core.files import File
from django.conf import settings
from os import path

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
       
class MyndighetsforeskriftAdmin(admin.ModelAdmin):
    list_display = ('fsnummer', 'titel','beslutad', 'ikrafttradandedag', 'utkom_fran_tryck', 'typ')
    list_filter = ('beslutad', 'ikrafttradandedag')
    ordering = ('-beslutad', 'titel')
    search_fields = ('titel', 'fsnummer',)

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
        published=datetime.now()

        # Se om det finns ett tidigare AtomEntry för denna föreskrift.
        try:
            foreskrift_entries=AtomEntry.objects.filter(foreskrift_id=obj.id).order_by("published")
            if foreskrift_entries:
                published=foreskrift_entries[0].published 
        except AtomEntry.DoesNotExist:
            # Kan inte hitta AtomEntry för denna föreskrift. Därmed är det en ny post.
            pass

        # Beräkna md5 för dokumentet
        md5=hashlib.md5()
        md5.update(open(obj.dokument.path, 'rb').read())
        dokument_md5=md5.hexdigest()

        # ...och för eventuell bilaga
        bilaga_md5 = ""
        bilaga_length = 0
        bilaga_uri = ""

        if obj.bilaga:
            md5=hashlib.md5()
            md5.update(open(obj.bilaga.path, 'rb').read())
            bilaga_md5=md5.hexdigest()
            bilaga_length = len(open(obj.bilaga.path, 'rb').read())
            bilaga_uri = obj.get_rinfo_uri() + "#bilaga-1"

        # ...och för metadataposten i RDF-format
        md5=hashlib.md5()
        rdfxml=obj.to_rdfxml()
        md5.update(rdfxml.encode("utf-8"))
        rdf_md5=md5.hexdigest()

        # Skapa AtomEntry-posten
        entry=AtomEntry(  foreskrift_id=obj.id,
                title=obj.titel,
                updated=datetime.now(),
                published=published,
                entry_id=obj.get_rinfo_uri(),
                content_md5=dokument_md5,
                content_src="/" + obj.dokument.url,
                enclosure_href=("/" + obj.bilaga.url) if obj.bilaga else None,
                enclosure_length=bilaga_length if obj.bilaga else None,
                enclosure_md5=bilaga_md5 if obj.bilaga else None,
                enclosure_uri=bilaga_uri if obj.bilaga else None,
                rdf_href=obj.get_absolute_url() + "rdf",
                rdf_length=len(rdfxml),
                rdf_md5=rdf_md5)

        # Spara AtomEntry för denna aktivitet
        entry.save()


# Registrera adminklasserna
admin.site.register(Amnesord, AmnesordAdmin)
admin.site.register(CelexReferens, CelexReferensAdmin)
admin.site.register(Forfattningssamling, ForfattningssamlingAdmin)
admin.site.register(Myndighetsforeskrift, MyndighetsforeskriftAdmin)
admin.site.register(Bemyndigandeparagraf)
admin.site.register(AtomEntry)
