# -*- coding: utf-8 -*-
# DUMMY Django settings for FST Web (fst_web).
from os import path

DEBUG = True
TEMPLATE_DEBUG = DEBUG


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(path.dirname(__file__), 'database/fst_demo.db').replace('\\','/') #Path to sqlite 3 db-file
    }
}

MEDIA_ROOT = path.join(path.dirname(__file__), 'uploads')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'skapa-en-egen-unik-nyckel'

# Webbplatsens adress och port (utan avslutande '/').
#FST_SITE_URL = "http://fst.lagrummet.se/fffs"
FST_SITE_URL = "http://127.0.0.1:8000"

# Organisationsinformation.
FST_ORG_NAME = u"Finansinspektionen"
FST_ORG_NAME_POSSESSIVE = u"Finansinpektionens"

# Kontaktinformation. Används i Atom-flödet.
FST_ORG_CONTACT_NAME = u"Jonas Beckman"
FST_ORG_CONTACT_URL = "http://www.fi.se/"
FST_ORG_CONTACT_EMAIL = "webmaster@fi.se"

# Datakällans beskrivning. Används i Atom-flödet. Erhålls från
# rättsinformationsprojektet.
FST_DATASET_URI = "tag:fi.se,2011:rinfo:feed"
FST_DATASET_TITLE = u"Flöde föFinansinspektionens författningssamling"

# Första delen av unik identifierare för dokument för denna organisation.
# Erhålls från rättsinformationsprojektet.
FST_PUBL_BASE_URI = "http://rinfo.lagrummet.se/publ/fffs/"

ADMINS = (
    # (FST_ORG_CONTACT_NAME, FST_ORG_CONTACT_EMAIL),
)

MANAGERS = ADMINS
