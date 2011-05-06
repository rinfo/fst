# -*- coding: UTF-8 -*-
from fabric.api import *

#def dev()
#def prod()

#def setup_host()

def hello():
    print("Hello world!")
    
def clean_db():
    local("rm -rf database/fst_demo.db;python manage.py syncdb --noinput;python manage.py loaddata fs_doc/fixtures/exempeldata.json")

def test():
    local("python manage.py test")
    
def clean_test():
    clean_db()
    test()


