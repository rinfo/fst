# coding=utf-8
from django.conf.urls.defaults import *

import os

# Slå på Djangos automatiska administrationssgränssnitt
from django.contrib import admin
admin.autodiscover()

# Konfigurera URL-routing

urlpatterns = patterns('',
    # Se till att filer i mappen static skickas
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static').replace('\\','/')}),

    # Se till att PDF-versionen av föreskrifter i mappen dokument skickas
    (r'^dokument/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'dokument').replace('\\','/')}),

    # Startsidan ("/")
    (r'^$', 'lagrumsapp.rinfo.views.index'),

    # Enskild föreskrift i RDF-format (t.ex. "/publ/RA-FS/2006:6/rdf"
    (r'^publ/(?P<fskortnamn>.*)/(?P<fsnummer>.*)/rdf$', 'lagrumsapp.rinfo.views.foreskrift_rdf'),

    # Enskild föreskrift (t.ex. "/publ/RA-FS/2006:6"
    (r'^publ/(?P<fskortnamn>.*)/(?P<fsnummer>.*)/$', 'lagrumsapp.rinfo.views.foreskrift'),

    # Indelade per ämnesord ("/amnesord/")
    (r'^amnesord/$', 'lagrumsapp.rinfo.views.amnesord'),

    # Indelade per ikraftträdandeår ("/artal/")
    (r'^artal/$', 'lagrumsapp.rinfo.views.artal'),

    # Atom-feed med ändringar i författningssamlingen
    (r'^feed/$', 'lagrumsapp.rinfo.views.atomfeed'),

    # Slå på administrationsgränssnitt
    (r'^admin/(.*)', admin.site.root),
)
