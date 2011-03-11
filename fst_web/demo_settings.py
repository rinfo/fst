# -*- coding: utf-8 -*-
# DUMMY Django settings for FST Web (fst_web).

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'skapa-en-egen-unik-nyckel'

# Webbplatsens adress och port (utan avslutande '/').
FST_SITE_URL = "http://127.0.0.1:8000"

# Organisationsinformation.
FST_ORG_NAME = u"Exempelmyndigheten"
FST_ORG_NAME_POSSESSIVE = u"Exempelmyndighetens"
# Unik identifierare i URI-format för organisationen som utfärdar föreskrifter
# i denna applikation. Erhålls från rättsinformationsprojektet.
FST_ORG_URI = "http://rinfo.lagrummet.se/org/exempelmyndigheten"

# Kontaktinformation. Används i Atom-flödet.
FST_ORG_CONTACT_NAME = u"Erik Exempelson"
FST_ORG_CONTACT_URL = "http://www.exempelmyndigheten.se/"
FST_ORG_CONTACT_EMAIL = "lagrum@exempelmyndigheten.se"

# Datakällans beskrivning. Används i Atom-flödet. Erhålls från
# rättsinformationsprojektet.
FST_DATASET_URI = "tag:exempelmyndigheten.se,2009:rinfo:feed"
FST_DATASET_TITLE = u"Flöde för Exempelmyndighetens författningssamling"

# Första delen av unik identifierare för dokument för denna organisation.
# Erhålls från rättsinformationsprojektet.
FST_PUBL_BASE_URI = "http://rinfo.lagrummet.se/publ/exfs/"

