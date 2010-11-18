from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import files, console
from fabric import utils
from fabric.operations import *

# globals
env.project_name = 'webme'
# environments
def environment():
    "Use the local virtual server"
    env.hosts = ['184.106.152.183']
    env.code_root = '/web/webme'
    env.user = 'webme'
    env.deploy_user = 'webme'
    env.virtualhost_code_root = "/"
    env.activate = 'source %s/bin/activate' %(env.code_root)
    
    
def virtualenv(command):
    with cd(env.code_root):
        sudo(env.activate + '&&' + command, user=env.deploy_user)
# tasks
def test():
    "Run the test suite and bail out if it fails"
    local("cd $(code_root); python manage.py test", fail="abort")
def setup():
    """
    Setup a fresh virtualenv as well as a few useful directories, then run
    a full deployment
    """
    require('hosts', provided_by=[environment])
    require('code_root')
    sudo('apt-get install -y python-setuptools')
    sudo('easy_install pip')
    sudo('pip install virtualenv')
    sudo('apt-get -y install git-core')
    sudo('aptitude install -y apache2')
    sudo('aptitude install -y libapache2-mod-wsgi')
    # we want rid of the defult apache config
    sudo('cd /etc/apache2/sites-available/; a2dissite default;')
    sudo('mkdir -p %s; cd %s; virtualenv .;source ./bin/activate'% (env.code_root, env.code_root))
    sudo('cd %s; mkdir releases; mkdir shared; mkdir packages;'% (env.code_root))
    deploy()
def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[environment])
    require('code_root')
    import time
    env.release = time.strftime('%Y%m%d%H%M%S')
    upload_tar_from_git()
    install_requirements()
    install_nonpython_requirements()
    configure_project_specific_stuff()
    install_site()
    symlink_current_release()
    migrate()
    restart_webserver()
def deploy_version(version):
    "Specify a specific version to be made live"
    require('hosts', provided_by=[environment])
    require('code_root')
    env.version = version
    run('cd $(%s); rm releases/previous; mv releases/current releases/previous;')
    run('cd $(%s); ln -s $(version) releases/current')
    restart_webserver()
def rollback():
    """
    Limited rollback capability. Simple loads the previously current
    version of the code. Rolling back again will swap between the two.
    """
    require('hosts', provided_by=[environment])
    require('code_root')
    run('cd $%s; mv releases/current releases/_previous;'% (env.code_root))
    run('cd $%s; mv releases/previous releases/current;'% (env.code_root))
    run('cd $%s; mv releases/_previous releases/previous;'% (env.code_root))
    restart_webserver()    
# Helpers. These are called by other functions rather than directly
def upload_tar_from_git():
    require('release', provided_by=[deploy, setup])
    "Create an archive from the current Git master branch and upload it"
    local('git archive --format=tar master | gzip > %s.tar.gz'% (env.release))
    sudo('mkdir %s/releases/%s'% (env.code_root, env.release))
    put('%s.tar.gz'%(env.release), '/tmp', mode=0755)
    sudo('mv /tmp/%s.tar.gz %s/packages/'%(env.release, env.code_root))
    sudo('cd %s/releases/%s && tar zxf ../../packages/%s.tar.gz'% (env.code_root,env.release, env.release ))
    local('rm %s.tar.gz'% (env.release))

def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    sudo('cd %s; pip install -E . -r ./releases/%s/requirements.txt'% (env.code_root, env.release))
    

def install_nonpython_requirements():
    "Install the required packages that cannot be installed with pip"
    require('code_root')
    sudo('cd %s/releases/current/%s/media_rsc/css; git clone git://github.com/joshuaclayton/blueprint-css.git'% (env.code_root, env.project_name))

def configure_project_specific_stuff():
    "Configure misc stuff for this project"
    require('code_root')
    put('/usr/local/lib/python2.6/dist-packages/django_socialregistration-0.4.2-py2.6.egg/socialregistration/views.py', '%s/src/socialregistration/socialregistration'% (env.code_root))
 
    
def install_site():
    "Add the virtualhost file to apache"
    require('release', provided_by=[deploy, setup])
    sudo('cd %s/releases/%s; cp %s /etc/apache2/sites-available/'% (env.code_root, env.release, env.project_name))
    sudo('cd /etc/apache2/sites-available/; a2ensite %s'% (env.project_name)) 

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    #sudo('cd %s; rm releases/previous; mv releases/current releases/previous;' % (env.code_root))
    sudo('cd %s; ln -s %s releases/current'% (env.code_root, env.release))
def migrate():
    "Update the database"
    require('project_name')
    sudo('cd %s/releases/current/;  ../../bin/python manage.py syncdb --noinput'% (env.code_root))
def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/apache2 restart')