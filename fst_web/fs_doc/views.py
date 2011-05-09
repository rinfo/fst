# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import  loader, Context, RequestContext
from django.utils.feedgenerator import rfc3339_date
from fst_web.fs_doc.models import Forfattningssamling, Myndighetsforeskrift, AllmannaRad, Amnesord, AtomEntry, RDFPost


def _response(request, template, context):
    return render_to_response(template, context, context_instance=RequestContext(request))


def index(request):
    """Display start page

    List the latest published documents in current document collection.
    Get both 'Myndighetsforeskrift' and 'AllmannaRad'.
    """

    latest_documents = list(Myndighetsforeskrift.objects.all().order_by("-utkom_fran_tryck")[:10]) + list(AllmannaRad.objects.all().order_by("-utkom_fran_tryck")[:10])

    return _response(request, 'index.html', locals())

def fs_dokument_rdf(request, fs_dokument_slug):
    """Display RDF representation of document"""

    rdf_post = get_object_or_404(RDFPost, slug=fs_dokument_slug)
    fs_dokument = rdf_post.content_object
    return HttpResponse(rdf_post.data, mimetype="application/rdf+xml; charset=utf-8")


def fs_dokument(request, fs_dokument_slug):
    """Display document subclassing 'FSDokument' """

    rdf_post = get_object_or_404(RDFPost, slug=fs_dokument_slug)
    fs_dokument = rdf_post.content_object
    if rdf_post.content_type.id == 9:
        return _response(request, 'allmanna_rad.html', dict(foreskrift=fs_dokument))
    elif rdf_post.content_type.id == 10:
        return _response(request, 'foreskrift.html', dict(foreskrift=fs_dokument))
    else:
        pass

def amnesord(request):
    """Display documents grouped by keywords """

    #foreskrifter = list(Myndighetsforeskrift.objects.all()) + list(AllmannaRad.objects.all())
    # Get all instances of 'Amnesord' used by at least one document
    #amnesord = list(Amnesord.objects.filter(myndighetsforeskrift__isnull = False).order_by("titel").distinct()) + list(Amnesord.objects.filter(allmannarad__isnull = False).order_by("titel").distinct())
    amnesord = Amnesord.objects.filter(
        myndighetsforeskrift__isnull = False).order_by("titel").distinct()

    return _response(request, 'per_amnesord.html', locals())

def artal(request):
    """Display documents grouped by year """

    foreskrifter = list(Myndighetsforeskrift.objects.all().order_by("-ikrafttradandedatum")) + list(AllmannaRad.objects.all().order_by("-ikrafttradandedatum"))

    return _response(request, 'per_ar.html', locals())

def atomfeed(request):
    """ Return Atom Feed representing activities in document collection """

    entries = AtomEntry.objects.order_by("-updated")
    last_updated = rfc3339_date(entries[0].updated) if entries else ""
    feed_id = settings.FST_DATASET_URI
    feed_title = settings.FST_DATASET_TITLE
    feed_contact_name = settings.FST_ORG_CONTACT_NAME
    feed_contact_url = settings.FST_ORG_CONTACT_URL
    feed_contact_email = settings.FST_ORG_CONTACT_EMAIL
    fst_site_url = settings.FST_SITE_URL

    template = loader.get_template('atomfeed.xml')
    context = Context(locals())

    return HttpResponse(template.render(context), mimetype="application/atom+xml; charset=utf-8")


