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

"""
If you start getting error messages 'Invalid HTTP_HOSTheader',
uncomment ALLOWED_HOSTS and add your own IP-address or domain.
"""
# ALLOWED_HOSTS = ['localhost', '127.0.0.1', xxx.xx.xx.xxx]

# Look for instance-specific settings
try:
    from .instance_settings import *
except ImportError:
    from .default_instance_settings import *

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

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
#MEDIA_URL = os.path.join("/", FST_INSTANCE_PREFIX,
#                         "dokument/")
MEDIA_URL = os.path.join("/dokument/")

# Site and port for hosting FST service (do not add ending '/').
FST_SITE_URL = "http://127.0.0.1:8000"


# Site and port of specific FST instance (do not add ending '/').
FST_INSTANCE_URL = os.path.join("http://127.0.0.1:8000",
                               FST_INSTANCE_PREFIX)
