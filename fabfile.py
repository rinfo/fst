# -*- coding: UTF-8 -*-
from fabric.api import *

def move_sampledocs_to_fixture():
    local("cp fs_doc/fixtures/foreskrift/*.pdf uploads/foreskrift/")
    local("cp fs_doc/fixtures/bilaga/*.pdf uploads/bilaga/")
    local("cp fs_doc/fixtures/allmanna_rad/*.pdf uploads/allmanna_rad/")
    
def clean_db():
    local("rm -rf database/fst_demo.db;python manage.py syncdb --noinput;python manage.py loaddata fs_doc/fixtures/exempeldata.json")

def test():
    local("python manage.py test")
    
def clean_test():
    move_sampledocs_to_fixture()
    clean_db()
    test()


