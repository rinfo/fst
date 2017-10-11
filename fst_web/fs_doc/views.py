# -*- coding: utf-8 -*-
"""View code for displaying different representations of FST data"""

from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.feedgenerator import rfc3339_date
from fst_web.fs_doc.models import KonsolideradForeskrift, AllmannaRad
from fst_web.fs_doc.models import Myndighetsforeskrift
from fst_web.fs_doc.models import AtomEntry, RDFPost


def _response(request, template, context):
    """Utility method for rendering custom view

    This method uses django shortcut utilities.
    See https://docs.djangoproject.com/en/1.10/topics/http/shortcuts/
    """
    return render_to_response(template, context)


def index(request):
    """Display start page"""

    return HttpResponseRedirect(reverse('admin:index'))


def fs_dokument_rdf(request, fs_dokument_slug):
    """Display RDF representation of document"""

    rdf_post = get_object_or_404(RDFPost, slug=fs_dokument_slug)
    return HttpResponse(
        rdf_post.data, content_type="application/rdf+xml;charset=utf-8")


def fs_dokument(request, fs_dokument_slug):
    """Display custom HTML view of document

    Select HTML template according to type of document.
    All documents are subclasses of FSDokument.
    """

    rdf_post = get_object_or_404(RDFPost, slug=fs_dokument_slug)
    document_content = rdf_post.content_object
    if isinstance(document_content, AllmannaRad):
        return _response(
            request,
            'allmanna_rad.html',
            dict(doc=document_content))
    elif isinstance(document_content, Myndighetsforeskrift):
        return _response(
            request,
            'foreskrift.html',
            dict(doc=document_content))
    elif isinstance(document_content, KonsolideradForeskrift):
        return _response(
            request,
            'konsoliderad_foreskrift.html',
            dict(doc=document_content))
    else:
        pass


def atomfeed(request):
    """ Display Atom Feed representing activities in document collection """

    entries = AtomEntry.objects.order_by("-updated")
    context = {
        'entries': AtomEntry.objects.order_by("-updated"),
        'last_updated': rfc3339_date(entries[0].updated) if entries else "",
        'feed_id': settings.FST_DATASET_URI,
        'feed_title': settings.FST_DATASET_TITLE,
        'feed_contact_name': settings.FST_ORG_CONTACT_NAME,
        'feed_contact_url': settings.FST_ORG_CONTACT_URL,
        'feed_contact_email': settings.FST_ORG_CONTACT_EMAIL,
        'fst_instance_url': settings.FST_INSTANCE_URL,
    }
    return HttpResponse(
        _response(request, 'atomfeed.xml', context),
        content_type="application/atom+xml; charset=utf-8")
