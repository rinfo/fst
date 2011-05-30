# -*- coding: UTF-8 -*-
from fabric.api import *

env.virtualenv = '/opt/rinfo/fst'

def launch_instance(name):
    create_instance(name)
    # TODO: add new row with WSGIScriptAlias in "/opt/rinfo/fst/fst.conf"
    restart_apache()

def create_instance(name):
    instances_dir = "%(virtualenv)s/instances" % env
    with cd(instances_dir):
        run("git clone git://github.com/rinfo/fst.git %s" % name)
    with cd("%(instances_dir)s/%(name)s/fst_web" % vars()):
        run("cp demo_settings.py local_settings.py")
        # TODO: configure local_settings.py
        run("python manage.py syncdb")
        run("chmod -R o+rw database uploads")

def stop_apache():
    sudo("apachectl stop")

def start_apache():
    sudo("apachectl start")

def restart_apache():
    sudo("apachectl restart")

def setup_env():
    # TODO: setup virtualenv
    # TODO: pip install -r requirements.txt (same for all instances)
    raise NotImplemented

def configure_apache():
    # TODO: rsync apache config files
    raise NotImplemented

