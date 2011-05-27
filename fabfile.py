# -*- coding: UTF-8 -*-
from fabric.api import *

def move_sampledocs_to_fixture():
    local("mkdir -p uploads/foreskrift")
    local("rm -f uploads/foreskrift/*.pdf")
    local("cp fs_doc/fixtures/foreskrift/*.pdf uploads/foreskrift/")
    
    local("mkdir -p uploads/bilaga")
    local("rm -f uploads/bilaga/*.pdf")
    local("cp fs_doc/fixtures/bilaga/*.pdf uploads/bilaga/")
    
    local("mkdir -p uploads/allmanna_rad")
    local("rm -f uploads/allmanna_rad/*.pdf")
    local("cp fs_doc/fixtures/allmanna_rad/*.pdf uploads/allmanna_rad/")
    
    local("mkdir -p uploads/konsoliderad_foreskrift")
    local("rm -f uploads/konsoliderad_foreskrift/*.pdf")
    local("cp fs_doc/fixtures/konsoliderad_foreskrift/*.pdf uploads/konsoliderad_foreskrift/")
    
def clean_db():
    local("rm -rf database/fst_demo.db;python manage.py syncdb --noinput;python manage.py loaddata fs_doc/fixtures/exempeldata.json")

def test():
    local("python manage.py test")
    
def clean_test():
    move_sampledocs_to_fixture()
    clean_db()
    test()


