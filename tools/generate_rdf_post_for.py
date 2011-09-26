#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from django.core.management import setup_environ
from fst_web import settings
setup_environ(settings)
from fst_web.fs_doc.models import Myndighetsforeskrift, AllmannaRad, \
    KonsolideradForeskrift, generate_rdf_post_for

for cls in (Myndighetsforeskrift, AllmannaRad, KonsolideradForeskrift):
    for obj in cls.objects.all():
        print "Generating rdf post for %s" % obj
        generate_rdf_post_for(obj)
    


