# -*- coding: UTF-8 -*-
from fabric.api import *
from fabric.contrib.project import rsync_project


env.instances_dir = "/opt/rinfo/fst/instances"
env.bak_path = "bak/opt-rinfo-fst-instances.tar.gz"
env.local_bak = "/opt/work/rinfo/fst/backup"


@task
def integ():
    """
    Set target env to INTEGRATION.
    """
    env.hosts = ["rinfo-fst"]

@task
def prod():
    """
    Set target env to PRODUCTION.
    """
    env.hosts = ["fst.lagrummet.se"]
    env.user = 'rinfo'


@task
def setup_server():
    sudo("apt-get install git")
    sudo("apt-get install python-dev")
    sudo("apt-get install python-pip")
    # TODO: setup virtualenv
    # TODO: pip install -r requirements.txt (same for all instances)


@task
def create_instance(name, version=None):
    """
    Create a new FST instance with the given ``name``.
    """
    with cd(env.instances_dir):
        run("git clone git://github.com/rinfo/fst.git %s" % name)

    with cd("%s/%s/fst_web" % (env.instances_dir, name)):
        if version:
            run("git checkout tags/%s" % version)

        run("cp demo_settings.py local_settings.py")

        print ".. Remember to edit local_settings.py"  # TODO:
        #''.join(
        # [choice(
        # 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
        # for i in range(50)])
        # s/Exempel/${GovName}/g
        # s/exempel/${govname}/g
        # s/exfs/${name}/g

        # you need no superuser; done in the next step
        run("python manage.py syncdb")

        # create user and rights
        # TODO: optionally pre-adjust:
        #run("cp fs_doc/fixtures/example_no_docs.json" +
        # "fs_doc/fixtures/initial_no_docs.json")
        # s/EXFS/${NewFs}/g
        print ".. Remember to rename the initial EXFS"
        run("python manage.py loaddata fs_doc/fixtures/example_no_docs.json")

        # allow apache to write to the database, upload and logs directory
        run("chmod -R o+rw database uploads logs")

    # TODO
    print '.. Remember to add new WSGIScriptAlias in "/opt/rinfo/fst/fst.conf"'
    #restart_apache()


@task
def ls():
    """
    List all FST instances.
    """
    run("ls -l %(instances_dir)s" % env)
    # TODO: name, version_tag, location


@task
def info(name):
    """
    Describe an FST instance.
    """
    raise NotImplementedError


@task
def bak():
    """
    Create a backup archive of all FST instances and download to ``local_bak``.
    """
    run("tar czvf %(bak_path)s %(instances_dir)s" % env)
    get(env.bak_path, env.local_bak)

@task
def stop_apache():
    sudo("apachectl stop")

@task
def start_apache():
    sudo("apachectl start")

@task
def restart_apache():
    sudo("apachectl restart")

