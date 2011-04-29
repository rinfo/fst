# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
import datetime
from fst_web.fs_doc.models import Myndighetsforeskrift, Forfattningssamling, Amnesord, AtomEntry,AllmannaRad
from django.utils.feedgenerator import rfc3339_date
from django.conf import settings
from django.template import loader, Context


def _response(request, template, context):
    return render_to_response(template, context, context_instance=RequestContext(request))


def index(request):
    """Show start page """

    senaste_myndighetsforeskrifter = Myndighetsforeskrift.objects.all().order_by("-utkom_fran_tryck")[:10]

    return _response(request, 'index.html', locals())

def foreskrift_rdf(request, fskortnamn, arsutgava, lopnummer):
    """Display RDF representation of document"""

    fs = get_object_or_404(Forfattningssamling,kortnamn=fskortnamn)
    foreskrift = get_object_or_404(Myndighetsforeskrift,arsutgava=arsutgava,lopnummer=lopnummer,forfattningssamling=fs)

    # Return RDF
    return HttpResponse(foreskrift.to_rdfxml(), mimetype="application/rdf+xml; charset=utf-8")


def allmanna_rad(request, fskortnamn, arsutgava, lopnummer):
    """Display document of type 'AllmannaRad' """

    fs = get_object_or_404(Forfattningssamling,kortnamn=fskortnamn)
    foreskrift = get_object_or_404(AllmannaRad,arsutgava=arsutgava,lopnummer=lopnummer,forfattningssamling=fs)

    return _response(request, 'foreskrift.html', locals())

def foreskrift(request, fskortnamn, arsutgava, lopnummer):
    """Display document of type 'Myndighetsforeskrift' """
    
    fs = get_object_or_404(Forfattningssamling,kortnamn=fskortnamn)
    foreskrift = get_object_or_404(Myndighetsforeskrift,arsutgava=arsutgava,lopnummer=lopnummer,forfattningssamling=fs)

    return _response(request, 'foreskrift.html', locals())

def amnesord(request):
    """Display documents grouped by keywords """

    # Get all instances of 'Amnesord' used by at least one document
    amnesord = Amnesord.objects.filter(myndighetsforeskrift__isnull = False).order_by("titel").distinct()

    return _response(request, 'per_amnesord.html', locals())

def artal(request):
    """Display documents grouped by year """

    foreskrifter = Myndighetsforeskrift.objects.all().order_by("-ikrafttradandedatum")

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


