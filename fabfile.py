"""
Distributor ID:	Ubuntu
Description:	Ubuntu 10.04 LTS
Release:	10.04
Codename:	lucid
"""

from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib import files, console
from fabric import utils
from fabric.operations import *

# globals
env.project_name = 'webme'

def environment():
    "Use the local virtual server"
    env.hosts = ['184.106.152.183']
    env.code_root = '/web/webme'
    # This is used to change permissions
    env.code_root_parent = "/web" 
    env.user = 'webme'
    env.deploy_user = 'webme'   
    env.activate = 'source %s/bin/activate' %(env.code_root)
    env.version = 1
    env.release = env.version
    
    
def virtualenv(command):
    with cd(env.code_root):
        sudo(env.activate + '&&' + command, user=env.deploy_user)
# tasks
def test():
    "Run the test suite and bail out if it fails"
    local("cd $(code_root); python manage.py test", fail="abort")

def reset_permissions():
    sudo('chown %s -R %s'% (env.user,env.code_root_parent))
    sudo('chgrp %s -R %s'% (env.user,env.code_root_parent))

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
    sudo('apt-get install libjpeg-dev zlib1g-dev')
    # we want rid of the defult apache config
    sudo('cd /etc/apache2/sites-available/; a2dissite default;')
    sudo('mkdir -p %s; cd %s; virtualenv .;source ./bin/activate'% (env.code_root, env.code_root))
    sudo('cd %s; mkdir releases; mkdir shared; mkdir packages;'% (env.code_root))
    reset_permissions()    
    deploy()
                                                                        

    
def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[environment])
    require('code_root')
    #import time
    env.release = env.version #time.strftime('%Y%m%d%H%M%S')
    # whole_path looks like /web/webme/releases/20202020202/webme
    env.whole_path = "%s/releases/%s/%s"%(env.code_root, env.release, env.project_name)
    upload_tar_from_git()
    install_requirements()
    install_nonpython_requirements()
    configure_project_specific_stuff()
    symlink_current_release()
    install_site()

    #migrate()
    restart_webserver()
    
def redeploy():
    """
    Redeploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and 
    then restart the webserver
    """
    require('hosts', provided_by=[environment])
    require('code_root')
    env.whole_path = "%s/releases/%s/%s"%(env.code_root, env.release, env.project_name)
    upload_tar_from_git()
    symlink_current_release()
    install_site()

    #migrate()
    restart_webserver()

def upload_tar_from_git():
    require('release', provided_by=[deploy, setup])
    require('whole_path', provided_by=[deploy, setup])
    "Create an archive from the current Git master branch and upload it"
    local('git archive --format=tar master | gzip > %s.tar.gz'% (env.release))
    sudo('mkdir -p %s'% (env.whole_path))
    put('%s.tar.gz'%(env.release), '/tmp', mode=0755)
    sudo('mv /tmp/%s.tar.gz %s/packages/'%(env.release, env.code_root))
    # After this last step the project is at:
    #   /web/webme/releases/20202020202/webme
    sudo('cd %s && tar zxf ../../../packages/%s.tar.gz'% (env.whole_path, env.release))
    sudo('chown %s -R %s'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s'% (env.user,env.whole_path))
    local('rm %s.tar.gz'% (env.release))
    
def install_requirements():
    "Install the required packages from the requirements file using pip"
    require('release', provided_by=[deploy, setup])
    require('whole_path', provided_by=[deploy, setup])
    sudo('cd %s; pip install -E . -r %s/requirements.txt'% (env.code_root,
                                                            env.whole_path))   
   
    reset_permissions()
                                                                          

def install_nonpython_requirements():
    "Install the required packages that cannot be installed with pip"
    require('code_root')
    require('whole_path', provided_by=[deploy, setup])
    sudo('cd %s/media_rsc/css; git clone git://github.com/joshuaclayton/blueprint-css.git'% (env.whole_path))
    sudo('chown %s -R %s'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s'% (env.user,env.whole_path))
    sudo('mkdir %s/lib; cd %s/lib; curl -O http://apache.mirrors.tds.net/lucene/solr/3.1.0/apache-solr-3.1.0.tgz' % (env.whole_path, env.whole_path))
    sudo('cd %s/lib; tar xvzf apache-solr-3.1.0.tgz' % (env.whole_path))
    sudo('chown %s -R %s/lib'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s/lib'% (env.user,env.whole_path))

def configure_project_specific_stuff():
    "Configure misc stuff for this project"
    require('code_root')
    require('whole_path', provided_by=[deploy, setup])
    put('/usr/local/lib/python2.6/dist-packages/django_socialregistration-0.4.2-py2.6.egg/socialregistration/views.py', '%s/src/socialregistration/socialregistration'% (env.code_root))
    sudo('chown %s -R %s'% (env.user,env.whole_path))
    sudo('chgrp %s -R %s'% (env.user,env.whole_path))

def symlink_current_release():
    "Symlink our current release"
    require('release', provided_by=[deploy, setup])
    #sudo('cd %s; rm releases/previous; mv releases/current releases/previous;' % (env.code_root))
    sudo('cd %s; ln -s %s releases/current; chown %s -R releases/current; chgrp %s -R releases/current'% (env.code_root, env.release, env.user, env.user))


def install_site():
    "Add the virtualhost file to apache"
    sudo('cd %s/releases/current/%s; cp %s /etc/apache2/sites-available/'% (env.code_root,
                                                                            env.project_name,
                                                                            env.project_name))
    sudo('cd /etc/apache2/sites-available/; a2ensite %s'% (env.project_name)) 
    

def restart_webserver():
    "Restart the web server"
    sudo('/etc/init.d/apache2 restart')
        
def migrate():
    "Update the database"
    require('project_name')
    sudo('cd %s/releases/current/;  ../../bin/python manage.py syncdb --noinput'% (env.code_root))
    

    
    
'''=========================================================='''
'''                    Unused Functions                      '''
'''=========================================================='''
    
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
    

