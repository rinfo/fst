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
    (r'^$', 'rinfo-foreskriftshantering.rinfo.views.index'),

    # Enskild föreskrift i RDF-format (t.ex. "/publ/RA-FS/2006:6/rdf"
    (r'^publ/(?P<fskortnamn>.*)/(?P<arsutgava>.*):(?P<lopnummer>.*)/rdf$', 'rinfo-foreskriftshantering.rinfo.views.foreskrift_rdf'),

    # Enskild föreskrift (t.ex. "/publ/RA-FS/2006:6"
    (r'^publ/(?P<fskortnamn>.*)/(?P<arsutgava>.*):(?P<lopnummer>.*)/$', 'rinfo-foreskriftshantering.rinfo.views.foreskrift'),

    # Indelade per ämnesord ("/amnesord/")
    (r'^amnesord/$', 'rinfo-foreskriftshantering.rinfo.views.amnesord'),

    # Indelade per ikraftträdandeår ("/artal/")
    (r'^artal/$', 'rinfo-foreskriftshantering.rinfo.views.artal'),

    # Atom-feed med ändringar i författningssamlingen
    (r'^feed/$', 'rinfo-foreskriftshantering.rinfo.views.atomfeed'),

    # Slå på administrationsgränssnitt
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/(.*)', admin.site.root),
)
