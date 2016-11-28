# -*- coding: utf-8 -*-
"""
General Django settings for FST webservice
"""
import os


ROOT = os.path.abspath(os.path.dirname(__file__))


def make_root_path(args):
    os.path.join(ROOT, *args)


# Read SECRET_KEY from file at project level
# To replace secret key with a new one, run:
# 'python manage.py generate_secret_key --replace'
PARENT_DIR = os.path.abspath(os.path.join(ROOT, os.pardir))
SECRET_FILE = os.path.join(PARENT_DIR, 'secretkey.txt')
with open(SECRET_FILE) as f:
    SECRET_KEY = f.read().strip()

# Encoding of files read from disk (template and initial SQL files).
FILE_CHARSET = 'utf-8'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Stockholm'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sv-se'

DATE_FORMAT = 'Y-m-d'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Generate this the same way for all rinfo instances!
MEDIA_ROOT = os.path.join(os.path.dirname(__file__), 'uploads')

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# NOTE! In Django 1.4 this replaces "ADMIN_MEDIA_PREFIX"
# URL prefix for admin static files -- CSS, JavaScript and images.
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (

)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    )

# Default. More documentaton here:
# http://docs.djangoproject.com/en/dev/ref/contrib/sites/
SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

ROOT_URLCONF = 'fst_web.urls'

WSGI_APPLICATION = 'fst_web.wsgi.application'

# Specify directory where logs can be found
LOG_DIR = (make_root_path('logs'))

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # Application specific here    'fst_web.fs_doc',
    'fst_web.fs_doc',
    'fst_web.adminplus',
    )

# Ensure that users are logged out automatically if inactive for
# specified time.
SESSION_SAVE_EVERY_REQUEST = True  # Refresh cookie on new activity
SESSION_COOKIE_AGE = 30 * 60   # Cookie expires after this number of seconds

# Specify how detailed log output you want
LOG_LEVEL = "WARNING"
DB_DEBUG_LEVEL = "WARNING"  # Silence noisy debug output

EMAIL_HOST_USER = None  # Email notifications are enabled in local settings

# MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES +
# ('debug_toolbar.middleware.DebugToolbarMiddleware',)
# INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
# INTERNAL_IPS = ('127.0.0.1',) #

# New for Django 1.4: list all possible password algorithms.
# Unless your application has very special security needs, default is fine.
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

# Look for instance-specific settings
# TODO: declare specific imports here
try:
    from .local_settings import *  # Use local settings if they exist
except ImportError:
    from .demo_settings import *  # else fall back to demo settings

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [make_root_path('templates')],
        'OPTIONS': {
            'debug': DEBUG,
            'loaders':
                ['django.template.loaders.filesystem.Loader',
                 'django.template.loaders.app_directories.Loader'
                 ],
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Project-specific:
                "fst_web.context_processors.add_request_vars",
                ],
            },
        },
]

# Setup standard logging: daily rotating files for requests, app logging,
# debbugging DB calls etc.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s \%(process)d %'
                      '(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
        },
    'handlers': {
        'console': {
            'level': '%s' % LOG_LEVEL,
            'class': 'logging.StreamHandler',
            },
        'app_handler': {
            'level': '%s' % LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'fst_web.app.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
            },
        'db_handler': {
            'level': '%s' % LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'fst_web.db.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'simple',
            },
        'request_handler': {
            'level': '%s' % LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'django_request.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'simple',
            }
    },
    'loggers': {
        '': {'handlers': ['app_handler'],
             'level': '%s' % LOG_LEVEL,
             'propagate': False
             },
        'django.request': {'handlers': ['request_handler'],
                           'level': '%s' % LOG_LEVEL,
                           'propagate': False},
        'django.db.backends': {
            'handlers': ['db_handler'],
            'level': DB_DEBUG_LEVEL,
            'propagate': False,
        }
    }
}

if EMAIL_HOST_USER:
    LOGGING['handlers']['mail_admins'] = {
        'level': 'ERROR',
        'class': 'django.utils.log.AdminEmailHandler',
        'include_html': False,
        }

    LOGGING['loggers']['django.request']['handlers'].append('mail_admins')
