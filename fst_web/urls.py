# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.conf.urls import url, include
from django.views.generic.base import TemplateView, RedirectView
from django.views.static import serve
from fst_web.fs_doc.views import index, fs_dokument_rdf, fs_dokument, atomfeed
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


class TextPlainView(TemplateView):
    def render_to_response(self, context, **kwargs):
        return super(TextPlainView, self).render_to_response(
            context, content_type='text/plain', **kwargs)

# Add admin enhancements from AdminPlus
#admin.site = AdminSitePlus()

# Enable Django admin autodiscovery
admin.autodiscover()

# URL-routing

urlpatterns = [
    # Get files from server
    url(r'^dokument/(?P<path>.*)$', serve,
         {'document_root': settings.MEDIA_ROOT.replace('\\', '/')}),

    # Display start page ("/")
    url(r'^$', index, name='index'),

    # Display specific document as RDF
    url(r'^publ/(?P<fs_dokument_slug>.*)/rdf$', fs_dokument_rdf),

    # Display info about specific document
    url(r'^publ/(?P<fs_dokument_slug>.*)/$', fs_dokument, name='fs_dokument'),

    # Display Atom feed with activity in document collection
    url(r'^feed/$', atomfeed),

    # Tell web crawlers how to behave via robots.txt
    url(r'^robots\.txt$', TemplateView,{'template': 'robots.txt', 'mimetype': 'text/plain'}),

    # Add application favicon. Gets rid of lots of annoying log messages.
    url(r'^favicon\.ico$', RedirectView, {'url': '/static/images/favicon.ico'}),

    # Enable Django admin
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += staticfiles_urlpatterns()
