# -*- coding: utf-8 -*-
import os

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *args: os.path.join(ROOT, *args)

""" Template for local settings of the FST webservice (fst_web)

Please edit this file and replace all generic values with values suitable to
your particular installation.
"""

# NOTE! Always set this to False before deploying
DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': path('database/fst_demo.db')
    }
}

LOG_LEVEL = "DEBUG"

#Enable this to override global DB Debug setting
#DB_DEBUG_LEVEL = "DEBUG"

# Setup mail server for sending email notifications.
# You can use any mail server you want.
# But a very simple way to get started is to use a gmail account.
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
#EMAIL_HOST_USER = 'your email'
#EMAIL_HOST_PASSWORD = 'your password'

# Admins specified here receive email notifications on critical errors.
# By default, this is the FST sysadmin at Domstolsverket.
# Feel free to add more names if you want your local sysadmin to
# receive the same notifications.
ADMINS = (
# ('Sysadmin at FST', 'sysadmin@fst.lagrummet.se',
# ('Sysadmin at your agency', 'sysadmin@your_agency.se',
#),
)

MANAGERS = ADMINS

# Prefix of default document collection of this instance
FST_INSTANCE_PREFIX = "exfs"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = os.path.join("/", FST_INSTANCE_PREFIX, "dokument/")

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2i!!@xy4goq72irz5ldb%gmogc4w&#bgx64j6q9%l)r9^4i-v-'

# Site and port for hosting FST service (do not add ending '/').
FST_SITE_URL = "http://127.0.0.1:8000"


# Site and port of specific FST instance (do not add ending '/').
FST_INSTANCE_URL = os.path.join("http://127.0.0.1:8000",
                                FST_INSTANCE_PREFIX)

# Organization authorized to publish these documents.
FST_ORG_NAME = u"Exempelmyndigheten"
FST_ORG_NAME_POSSESSIVE = u"Exempelmyndighetens"

# Contact information for ATOM feed
FST_ORG_CONTACT_NAME = u"Erik Exempelson"
FST_ORG_CONTACT_URL = "http://www.exempelmyndigheten.se/"
FST_ORG_CONTACT_EMAIL = "lagrum@exempelmyndigheten.se"

# Description of data source for Atom feed.
# These values will be supplied by Rättsinformationsprojektet.
FST_DATASET_URI = "tag:exempelmyndigheten.se,2009:rinfo:feed"
FST_DATASET_TITLE = u"Flöde för Exempelmyndighetens författningssamling"
