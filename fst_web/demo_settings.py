# -*- coding: utf-8 -*-
import os
ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *args: os.path.join(ROOT, *args)

# These are the default DEMO settings for FST webservice (fst_web)
# Replace this file with a file named 'local_settings.py' for production use


# NOTE! Always set this to FALSE before deploying
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path.join(path.dirname(__file__),
                          'database/fst_demo.db').replace('\\','/')
        #Path to sqlite 3 db-file
    }
}

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2i!!@xy4goq72irz5ldb%gmogc4w&#bgx64j6q9%l)r9^4i-v-'

# Webbplatsens adress och port (utan avslutande '/').
FST_SITE_URL = "http://127.0.0.1:8000"

# Organisationsinformation.
FST_ORG_NAME = u"Exempelmyndigheten"
FST_ORG_NAME_POSSESSIVE = u"Exempelmyndighetens"

# Kontaktinformation. Används i Atom-flödet.
FST_ORG_CONTACT_NAME = u"Erik Exempelson"
FST_ORG_CONTACT_URL = "http://www.exempelmyndigheten.se/"
FST_ORG_CONTACT_EMAIL = "lagrum@exempelmyndigheten.se"

# Datakällans beskrivning. Används i Atom-flödet. Erhålls från
# rättsinformationsprojektet.
FST_DATASET_URI = "tag:exempelmyndigheten.se,2009:rinfo:feed"
FST_DATASET_TITLE = u"Flöde för Exempelmyndighetens författningssamling"
