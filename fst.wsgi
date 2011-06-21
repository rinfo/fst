# Include from main apache config like this:
#
#    WSGIScriptAlias /dvfs /opt/rinfo/fst/instances/dvfs/fst.wsgi
#
# See https://github.com/rinfo/fst/wiki/Deployment for more information

import os
import sys

path = os.path.dirname(__file__)
if path not in sys.path:
    sys.path.append(path)

subpath = path + os.sep + "fst_web"
if subpath not in sys.path:
    sys.path.append(subpath)

os.environ['DJANGO_SETTINGS_MODULE'] = 'fst_web.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
