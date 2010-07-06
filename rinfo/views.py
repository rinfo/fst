# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
import datetime
from rinfo.models import Myndighetsforeskrift, Forfattningssamling, Amnesord, AtomEntry
from django.utils.feedgenerator import rfc3339_date
from django.conf import settings
from django.template import loader, Context

def index(request):
    """Visa startsidan."""

    #Senast utgivna (då de utkom från tryck)
    senaste_myndighetsforeskrifter = Myndighetsforeskrift.objects.all().order_by("-utkom_fran_tryck")[:10]

    return render_to_response('index.html', locals())


def foreskrift_rdf(request, fskortnamn, arsutgava, lopnummer):
    """Visa RDF-data för enskild föreskrift i författningssamling."""

    # Hämta författningssamlingen
    fs = Forfattningssamling.objects.get(kortnamn=fskortnamn)
    # Hämta föreskriften
    identifierare = "%s %s:%s" % (fskortnamn, arsutgava, lopnummer)
    foreskrift = Myndighetsforeskrift.objects.get(identifierare=identifierare, forfattningssamling=fs)

    # Skicka rdf-data för denna post
    return HttpResponse(foreskrift.to_rdfxml(), mimetype="application/rdf+xml; charset=utf-8") 



def foreskrift(request, fskortnamn, arsutgava, lopnummer):
    """Visa enskild föreskrift i författningssamling."""

    # Hämta författningssamlingen
    fs = Forfattningssamling.objects.get(kortnamn=fskortnamn)
    # Hämta föreskriften
    identifierare = "%s %s:%s" % (fskortnamn, arsutgava, lopnummer)
    foreskrift = Myndighetsforeskrift.objects.get(identifierare=identifierare, forfattningssamling=fs)

    return render_to_response('foreskrift.html', locals())



def amnesord(request):
    """Visa föreskrifter indelade efter ämnesord."""

    # Hämta alla ämnesord som har minst en föreskrift kopplad
    amnesord = Amnesord.objects.filter(myndighetsforeskrift__isnull = False).order_by("titel").distinct()

    return render_to_response('per_amnesord.html', locals())



def artal(request):
    """Visa föreskrifter indelade efter ikraftträdandeår."""

    foreskrifter = Myndighetsforeskrift.objects.all().order_by("-ikrafttradandedatum")

    return render_to_response('per_ar.html', locals())


def atomfeed(request):
    """Presentera en postförteckning över aktiviteter i författningssamlingen i
    Atom-format."""

    entries = AtomEntry.objects.order_by("-updated")
    last_updated = rfc3339_date(entries[0].updated) if entries else ""
    feed_uri = settings.RINFO_FEED_URI
    feed_title = settings.RINFO_FEED_TITLE
    feed_contact_name = settings.RINFO_FEED_CONTACT_NAME
    feed_contact_url = settings.RINFO_FEED_CONTACT_URL
    feed_contact_email = settings.RINFO_FEED_CONTACT_EMAIL
    rinfo_site_url = settings.RINFO_SITE_URL

    template = loader.get_template('atomfeed.xml')
    context = Context(locals())

    return HttpResponse(template.render(context), mimetype="application/atom+xml; charset=utf-8") 
    





