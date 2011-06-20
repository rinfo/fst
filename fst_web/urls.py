# -*- coding: utf-8 -*-
import os
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from adminplus import AdminSitePlus

# Add admin enhancements from AdminPlus
admin.site = AdminSitePlus()

# Enable Django admin autodiscovery
admin.autodiscover()

# URL-routing

urlpatterns = patterns('',
                       # Display static files
                       (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static').replace('\\','/')}),

                       # Get files from server
                       (r'^\w*/dokument/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT.replace('\\','/')}),

                       # Display start page ("/")
                       (r'^$', 'fst_web.fs_doc.views.index'),

                       # Display specific document as RDF
                       (r'^publ/(?P<fs_dokument_slug>.*)/rdf$', 'fst_web.fs_doc.views.fs_dokument_rdf'),

                       # Display info about specific document
                       (r'^publ/(?P<fs_dokument_slug>.*)/$', 'fst_web.fs_doc.views.fs_dokument'),

                       # Display Atom feed with activity in document collection
                       (r'^feed/$', 'fst_web.fs_doc.views.atomfeed'),

                       # Enable Django admin
                       (r'^admin/', include(admin.site.urls)),
                       #(r'^admin/(.*)', admin.site.root),
)
