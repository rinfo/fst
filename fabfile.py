# -*- coding: UTF-8 -*-
import os.path
from fabric.api import *
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project


env.fst_dir = "/opt/rinfo/fst"
env.instances_dir = "%(fst_dir)s/instances" % env
env.fst_apache_conf = "%(fst_dir)s/fst.conf" % env

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
def setup_server():
    sudo("apt-get update")
    sudo("apt-get install curl -y")
    sudo("apt-get install apache2 -y")
    sudo("apt-get install libapache2-mod-wsgi -y")
    sudo("apt-get install python-dev -y")
    sudo("apt-get install python-pip -y")
    sudo("pip install virtualenv")
    sudo("apt-get install git -y")
    configure_apache()

@task
def configure_apache():
    """
    Set up apache2 configuration for FST.
    """
    sudo("a2enmod rewrite")
    sudo("a2enmod ssl")
    sudo("a2ensite default-ssl")
    upload_apache_conf()
    restart_apache()

@task
def upload_apache_conf():
    script_dir = os.path.dirname(__file__)
    configs = [
        ("deploy/apache2/sites-available/default", "/etc/apache2/sites-available/"),
        ("deploy/apache2/sites-available/default-ssl", "/etc/apache2/sites-available/"),
        ("deploy/apache2/httpd.conf", "/etc/apache2/"),
    ]
    for path, dest in configs:
        localpath = os.path.join(script_dir, *path.split('/'))
        put(localpath, dest, use_sudo=True)

@task
def setup_env(name="venv-default"):
    venv_dir = "%s/%s" % (env.fst_dir, name)
    make_user_dir(env.fst_dir)
    if not exists(venv_dir):
        run("virtualenv --distribute %s" % venv_dir)
    return venv_dir

@task
def create_instance(name, version=None, develop=True):
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
        if develop:
            run("git checkout develop")
        if version:
            run("git checkout tags/%s" % version)

    with cd(clone_dir):
        with prefix("source %s/bin/activate" % venv_dir):
            # TODO: updates for all instances!
            run("pip install -r requirements.txt")

            # you need no superuser; done in the next step
            run("python manage.py syncdb --noinput")
        with cd("%s/fst_web" % clone_dir):
            with prefix("source %s/bin/activate" % venv_dir):

                if exists("local_settings.py"):
                    run("cp local_settings.py local_settings.py.bak")

                run("cp demo_settings.py local_settings.py")

                # allow apache to write to the database, upload and logs directory
                # FIXME: set correct user and perms:
                #run("chown -R www-data database uploads logs")
                #run("chmod -R u+rw database uploads logs")
                run("chmod -R o+rw database uploads logs")

                print ".. Remember to edit local_settings.py"  # TODO:
                #import string as S
                #print ''.join([choice(S.ascii_lowercase + S.digits + '!@#$%^&*(-_=+)')
                #        for i in range(50)])
                # s/Exempel/${OrgName}/g
                # s/exempel/${orgname}/g
                # s/exfs/${series}/g
                # FIXME: and change debug to False!

    # TODO
    print '.. Remember to add new WSGIScriptAlias in ' + env.fst_apache_conf
    #restart_apache()


@task
def load_example_data(name):
    """
    Load example setup data fixture into named instance.
    """
    venv_dir = "%s/%s" % (env.fst_dir, name)
    clone_dir = env.instances_dir + "/" + name
    with cd(clone_dir):
        with prefix("source %s/bin/activate" % venv_dir):
            # create user and rights
            # TODO: optionally pre-adjust:
            #run("cp fs_doc/fixtures/example_no_docs.json" +
            # "fs_doc/fixtures/initial_no_docs.json")
            # s/EXFS/${NewFs}/g
            print ".. Remember to rename the initial EXFS"
            run("python manage.py loaddata "
                "fst_web/fs_doc/fixtures/exempeldata.json")


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
def bak(download='1'):
    """
    Create a backup archive of all FST instances and download to ``local_bak``.
    """
    run("tar czvf %(bak_path)s %(instances_dir)s %(fst_apache_conf)s" % env)
    if int(download):
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

