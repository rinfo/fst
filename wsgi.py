""" WSGI application settings for FST instance

The default setup at Domstolsverket assumes that instances of FST run
under the default virtualenv unless something else is explicitly specified.
"""
import os
import sys
import site

# Change this to match your production server path!
VIRTUALENV_PATH = '/opt/rinfo/fst/venv-default'
PYTHON_SITE_PACKAGES = 'lib/python2.7/site-packages'
# Specify the site-packages folder of your virtualenv
ALLDIRS = [os.path.join(VIRTUALENV_PATH, PYTHON_SITE_PACKAGES)]

# Redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr
prev_sys_path = list(sys.path)

# Add all third-party libraries from your virtualenv
for directory in ALLDIRS:
    site.addsitedir(directory)
# Reorder sys.path so new directories come first.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

# Activate the virtualenv
activate_this = os.path.join(VIRTUALENV_PATH, 'bin/activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

# Some more path trickery...
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

# Get the default settings
from django.conf import settings
os.environ["DJANGO_SETTINGS_MODULE"] = "fst_web.settings"

# Make sure both project and app are on sys.path
path = os.path.dirname(__file__)
subpath = path + os.sep + "fst_web"
if subpath not in sys.path:
    sys.path.insert(0, subpath)
if path not in sys.path:
    sys.path.insert(0, path)

# Finally... run our Django app under WSGI!
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
