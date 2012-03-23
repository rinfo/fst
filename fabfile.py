# -*- coding: UTF-8 -*-
from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project


env.fst_dir = "/opt/rinfo/fst/"
env.instances_dir = "%(fst_dir)s/instances" % env

env.bak_path = "bak/opt-rinfo-fst-instances.tar.gz"
env.local_bak = "/opt/work/rinfo/fst/backup"

def make_user_dir(dirpath):
    sudo("mkdir -p %s" % dirpath)
    sudo("chown -R %s %s" % (env.user, dirpath))


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
def prod2():
    """
    Set target env to PENDING NEW PRODUCTION.
    """
    env.hosts = ["fst-rinfo.oort.to"]
    env.user = 'rinfo'

@task
def setup_server():
    sudo("apt-get update")
    sudo("apt-get install curl -y")
    sudo("apt-get install apache2 -y")
    sudo("apt-get install libapache2-mod-wsgi -y")
    sudo("apt-get install python-dev -y")
    sudo("apt-get install python-pip -y")
    sudo("pip install virtualenv")
    sudo("apt-get install git -y")

@task
def setup_env(name="venv-default"):
    venv_dir = "%s/%s" % (env.fst_dir, name)
    make_user_dir(env.fst_dir)
    if not exists(venv_dir):
        run("virtualenv --distribute %s" % venv_dir)
    return venv_dir

@task
def create_instance(name, version=None):
    """
    Create a new FST instance with the given ``name``.
    """

    venv_dir = setup_env()

    make_user_dir(env.instances_dir)
    clone_dir = env.instances_dir + "/" + name

    if not exists(clone_dir):
        with cd(env.instances_dir):
            run("git clone git://github.com/rinfo/fst.git %s" % name)

    with cd(clone_dir):
        run("git pull")
        if version:
            run("git checkout tags/%s" % version)

    with cd(clone_dir):
        with prefix("source %s/bin/activate" % venv_dir):
            # TODO: updates for all instances!
            run("pip install -r requirements.txt")

    with cd("%s/fst_web" % clone_dir):

        with prefix("source %s/bin/activate" % venv_dir):

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

