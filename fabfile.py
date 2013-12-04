# -*- coding: UTF-8 -*-
import os.path
from fabric.api import *
from fabric.contrib.files import exists


env.fst_dir = "/opt/rinfo/fst"
env.instances_dir = "%(fst_dir)s/instances" % env
env.fst_apache_conf = "%(fst_dir)s/fst.conf" % env

env.bak_path = "bak/opt-rinfo-fst-instances.tar.gz"
env.local_bak = "/opt/work/rinfo/fst/backup"


def make_user_dir(dirpath):
    sudo("mkdir -p %s" % dirpath)
    sudo("chown %s %s" % (env.user, dirpath))


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
def fst_dev():
    """
    Set target env to FST_DEV.
    """
    env.hosts = ["109.74.8.81"]
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
        ("deploy/apache2/sites-available/default",
         "/etc/apache2/sites-available/"),
        ("deploy/apache2/sites-available/default-ssl",
         "/etc/apache2/sites-available/"),
        ("deploy/apache2/httpd.conf", "/etc/apache2/"),
    ]
    for path, dest in configs:
        localpath = os.path.join(script_dir, *path.split('/'))
        put(localpath, dest, use_sudo=True)


@task
def manual_python():
    """
    Print instructions for compiling Python on a Debian Linux.
    """
    print "Install reasonable dependencies for Python:"
    print "$ apt-get install dpkg-dev zlib1g-dev libbz2-dev libexpat1-dev "
    print "$ apt-get install libncurses5-dev libreadline6-dev libsqlite3-dev"
    print "$ apt-get install  libssl-dev"
    print "Download and compile Python 2.7:"
    print "$ cd ~/installers/"
    print "$ curl -O http://python.org/ftp/python/2.7.6/Python-2.7.6.tar.bz2"
    print "$ tar xjvf Python-2.7.6.tar.bz2"
    print "$ cd Python-2.7.6/"
    print "$ ./configure"
    print "$ make"
    print "$ sudo make install"
    print "Install distribute and virtualenv:"
    print "$ cd ~/installers/"
    print "$ curl -O http://python-distribute.org/distribute_setup.py"
    print "$ sudo python distribute_setup.py"
    print "$ sudo easy_install virtualenv"


@task
def setup_env(name="venv-default"):
    venv_dir = "%s/%s" % (env.fst_dir, name)
    make_user_dir(env.fst_dir)
    if not exists(venv_dir):
        run("virtualenv --distribute %s" % venv_dir)
    return venv_dir


@task
def update_instance(name, version=None, develop=True):
    """
    Update exsisting FST instance with specified 'name'.
    """
    venv_dir = setup_env()
    clone_dir = env.instances_dir + "/" + name
    if not exists(clone_dir):
        print "Found no instance named: " + name
    else:
        with cd(clone_dir):
            run("git pull")
            if develop:
                run("git checkout develop")
            if version:
                run("git checkout tags/%s" % version)



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
        with prefix("source %s/bin/activate" % venv_dir):
            run("pip install -r requirements.txt")


    with cd(clone_dir):
        run("git pull")
        if develop:
            run("git checkout develop")
        if version:
            run("git checkout tags/%s" % version)

    with cd(clone_dir):
        with prefix("source %s/bin/activate" % venv_dir):
            run("pip install -r requirements.txt")

            if not exists("fst_web/local_settings.py"):
                run("cp fst_web/demo_settings.py fst_web/local_settings.py")
            else:
                print "Warning! Using demo version of local settings."

            instance_settings_file = \
                "%s/deploy/instance_settings/%s/instance_settings.py" % \
                (clone_dir, name)
            default_settings_file = \
                "%s/deploy/instance_settings/default/instance_settings.py" % \
                (clone_dir)
            print instance_settings_file
            if exists(instance_settings_file):
                run("cp %s %s/fst_web/instance_settings.py" %
                    (instance_settings_file, clone_dir))
            else:
                print "No instance_settings found. Using default settings"
                run("cp %s %s/fst_web/instance_settings.py" %
                    (default_settings_file, clone_dir))


            with cd("%s/fst_web" % clone_dir):
                # Generate secret key and add to settings file
                secret = "SECRET_KEY = '%s'" % generate_secret_key()
                sudo("echo \"" + secret +  "\" >>  instance_settings.py")
                 # FIXME: and change debug to False!

            # Load FST default users and permissions
            run("python manage.py syncdb --noinput") # Don't create superuser here!
            run("python manage.py loaddata " +
                        "fst_web/database/default_users.json")

            with cd("%s/fst_web" % clone_dir):
                # allow apache to write database, upload and logs directory
                sudo("chown -R www-data database uploads logs")
                sudo("chmod -R a-w,u+rw database uploads logs")

    # Create middleware configuration for this instance
    sudo("chmod -R 666 " + env.fst_apache_conf)
    new_wsgi_alias = \
        "WSGIScriptAlias /%s  /opt/rinfo/fst/instances/%s/wsgi.py" %\
        (name, name)
    # Append new instance at the end of configuration file.
    sudo("echo  \"" + new_wsgi_alias + "\" >> " + env.fst_apache_conf)

    restart_apache()


def generate_secret_key():
    """
    Generate random string for use in settings file
    """
    from random import random
    from string import ascii_lowercase

    lis = list(ascii_lowercase)
    return "".join([lis[int(random() * 26)] for _ in xrange(50)])


@task
def load_example_data(name):
    """
    Load example setup data fixture into named instance.
    """
    venv_dir = "%s/%s" % (env.fst_dir, name)
    clone_dir = env.instances_dir + "/" + name
    with cd(clone_dir):
        with prefix("source %s/bin/activate" % venv_dir):
            # Setup users and access permissions
            run("python manage.py loaddata "
                "fst_web/fs_doc/database/default_users.json")


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
    sudo("apachectl stop")
    sudo("apachectl start")
