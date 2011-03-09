# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin
import os

# Slå på Djangos automatiska administrationssgränssnitt
admin.autodiscover()

# Konfigurera URL-routing

urlpatterns = patterns('',
    # Se till att filer i mappen static skickas
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static').replace('\\','/')}),

    # Se till att PDF-versionen av föreskrifter i mappen dokument skickas
    (r'^dokument/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'dokument').replace('\\','/')}),

    # Startsidan ("/")
    (r'^$', 'fst_web.fs_doc.views.index'),

    # Enskild föreskrift i RDF-format (t.ex. "/publ/RA-FS/2006:6/rdf"
    (r'^publ/(?P<fskortnamn>.*)/(?P<arsutgava>.*):(?P<lopnummer>.*)/rdf$', 'fst_web.fs_doc.views.foreskrift_rdf'),

    # Enskild föreskrift (t.ex. "/publ/RA-FS/2006:6"
    (r'^publ/(?P<fskortnamn>.*)/(?P<arsutgava>.*):(?P<lopnummer>.*)/$', 'fst_web.fs_doc.views.foreskrift'),

    # Indelade per ämnesord ("/amnesord/")
    (r'^amnesord/$', 'fst_web.fs_doc.views.amnesord'),

    # Indelade per ikraftträdandeår ("/artal/")
    (r'^artal/$', 'fst_web.fs_doc.views.artal'),

    # Atom-feed med ändringar i författningssamlingen
    (r'^feed/$', 'fst_web.fs_doc.views.atomfeed'),

    # Slå på administrationsgränssnitt
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/(.*)', admin.site.root),
)
