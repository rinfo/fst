# -*- coding: UTF-8 -*-
from fabric.api import *

def reset():
    move_sampledocs_to_fixture()
    reset_db()

def move_sampledocs_to_fixture():
    local("mkdir -p uploads/foreskrift")
    local("rm -f uploads/foreskrift/*.pdf")
    local("cp fs_doc/fixtures/foreskrift/*.pdf uploads/foreskrift/")

    local("mkdir -p uploads/bilaga")
    local("rm -f uploads/bilaga/*.pdf")
    local("cp fs_doc/fixtures/bilaga/*.pdf uploads/bilaga/")

    local("mkdir -p uploads/ovrigt")
    local("rm -f uploads/ovrigt/*.pdf")
    local("cp fs_doc/fixtures/ovrigt/*.pdf uploads/ovrigt/")

    local("mkdir -p uploads/allmanna_rad")
    local("rm -f uploads/allmanna_rad/*.pdf")
    local("cp fs_doc/fixtures/allmanna_rad/*.pdf uploads/allmanna_rad/")

    local("mkdir -p uploads/konsoliderad_foreskrift")
    local("rm -f uploads/konsoliderad_foreskrift/*.pdf")
    local("cp fs_doc/fixtures/konsoliderad_foreskrift/*.pdf "
          "uploads/konsoliderad_foreskrift/")

def clear_db(flags=""):
    local("rm -f database/fst_demo.db && python manage.py syncdb %s" % flags)

def reset_db(fixture_name="exempeldata"):
    clear_db("--noinput")
    local("python manage.py loaddata fs_doc/fixtures/%s.json" % fixture_name)

def reset_test():
    reset()
    test()

def test():
    local("python manage.py test")

def make_fixture(name):
    local("python manage.py dumpdata --indent 4 "
          " --exclude admin --exclude sessions.session "
          " --exclude contenttypes.contenttype --exclude fs_doc.atomentry "
          " > fs_doc/fixtures/%s.json" % name)

