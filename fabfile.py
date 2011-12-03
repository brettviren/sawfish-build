#!/usr/bin/env python

from fabric.api import local, abort, warn, env
from fabric.context_managers import lcd,cd
from fabric.operations import sudo as fabric_sudo
from fabric.contrib.files import exists
from glob import glob
import os, re

# On Debian Wheezy /bin/sh is dash which does not honor the "#!
# /bin/bash" in the "libtool" script.  So, tell the build systems to
# use /bin/bash instead of /bin/sh
os.environ['CONFIG_SHELL'] = '/bin/bash'

env.hosts = ['localhost']
all_projects = [ 'librep','rep-gtk','sawfish' ]

def sudo(cmd):
    '''Work around http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=639391'''
    username = os.environ['USER']
    refcount_file = '/dev/shm/ecryptfs-%s-Private' % username
    if os.path.exists(refcount_file):
        fp = open(refcount_file,'r')
        count = int(fp.readlines()[0].strip())
        fp.close()
        count += 1
        fp = open(refcount_file,'w')
        fp.write('%d\n'%count)
        fp.close()
        print ('Incremented ecryptfs ref count to %d to protect against Debian bug 639391.' % count)
    return fabric_sudo(cmd)
    

def list(): 
    'List what projects are supported'
    print ' '.join(all_projects)
def dependencies():
    'Install some of the dependencies needed'
    deps = ['dh-autoreconf', 
            'gettext',
            'autoconf',
            'libltdl-dev',
            'automake',
            'libtool',
            'autotools-dev',
            'gcc',
            'libreadline-dev',
            'readline-common',
            'libffi-dev',
            'libgdbm-dev',
            'libgmp3-dev',
            'libgtk2.0-dev',
            'libpango1.0-0',
            'libgnutls-dev',
            'quilt',
            ]
    sudo('apt-get -y install %s' % ' '.join(deps))
    return

def rebase():
    'Update the git repositories'
    for proj in all_projects:
        local('cd %s && git fetch'%proj)

def version_exist(project,version):
    'Determine if project has given version, return the tag'
    tag = version
    if project == 'sawfish' and 'sawfish' not in version:
        tag = 'sawfish-%s' % version
    with lcd(project):
        tags = local('git tag',True)
        tags = tags.split('\n')
        if tag in tags: 
            return tag
 
    abort( 'Project "%s" has not such tag "%s"' % (project,tag))
        
def latest(project):
    'Find the latest version for a project'
    pattern = '^%s-\d+\.\d+\.\d+$' % project

    highest = None
    with lcd(project):
        for tag in local('git tag',True).split('\n'):
            m = re.search(pattern,tag)
            if m is None: 
                continue
            highest = tag
            continue
        pass
    highest = highest[len('%s-'%project):]

    print ('The latest version of "%s" is "%s"' % (project,highest))

    return highest

def diff(project):
    'Make a diff'
    with lcd(project):
        patch = local('git diff',True)
        print (patch)
        pass
    return

def checkout(project,version):
    'usage: checkout project based on version tag'
    tag = version_exist(project,version)

    with lcd(project):
        branches = local('git branch -a',True)
        if tag in branches.split():
            if '* %s'%tag in branches.split('\n'):
                print('Branch "%s" already exists and is checked out' % tag)
                return
            local('git checkout %s' % tag)
            return
        local('git checkout -b %s %s' % (tag,tag))
        return

def checkout_branch(project,branch):
    'usage: checkout project based on branch'

    with lcd(project):
        branches = local('git branch -a',True)
        if branch in branches.split():
            if '* %s'%branch in branches.split('\n'):
                print('Branch "%s" already exists and is checked out' % branch)
                return
            local('git checkout %s' % branch)
            return
        local('git checkout -b %s remotes/origin/%s' % (branch,branch))
        return

def build_stepwise(project):
    'Build the Debian packages for the given project'
    with lcd(project):
        local('fakeroot ./debian/rules build-indep')
        local('fakeroot ./debian/rules build-arch')
        local('fakeroot ./debian/rules binary')
    return

def build(project):
    'Build the Debian packages for the given project'
    with lcd(project):
        local('dpkg-buildpackage -rfakeroot')

def clean(project):
    'Clean the Debian packages for the given project'
    with lcd(project):
        local('fakeroot ./debian/rules clean')
    return

def install(project,version):
    'Install packages for project of given version'
    packages = {
        'librep':
            ['librep[0-9]*_%(version)s-1nano_i386.deb',
             'librep-dev_%(version)s-1nano_i386.deb',
             'rep_%(version)s-1nano_i386.deb',
             'rep-doc_%(version)s-1nano_all.deb',],
        'rep-gtk':
            ['rep-gtk_%(version)s-1nano_i386.deb',],
        'sawfish':
            ['sawfish-data_%(version)s-1nano_all.deb',
             'sawfish_%(version)s-1nano_i386.deb',
             'sawfish-lisp-source_%(version)s-1nano_all.deb']
        }

    pkgs = [glob(pkg%{'version':version})[0] for pkg in packages[project]]

    with cd(os.environ['PWD']):
        for pkg in pkgs:
            assert exists(pkg), 'Package file "%s" does not exist' % pkg
            continue
        sudo('dpkg -i %s' % ' '.join(pkgs))

    return

def uninstall(project):
    'Uninstall all packages for project'
    packages = {
        'librep':
            ['librep-dev','rep','rep-doc'],
        'rep-gtk':
            ['rep-gtk'],
        'sawfish':
            ['sawfish-data', 'sawfish', 'sawfish-lisp-source'],
        }
    sudo('apt-get -y -m remove --purge %s' % ' '.join(packages[project]))


def ucbi(project,version):
    'Uninstall, Clean, Build and Install version of project'
    uninstall(project)
    clean(project)
    build(project)
    install(project,version)

def clone(project):
    'git clone a project'
    if os.path.exists(os.path.join(project,'.git')):
        print ('Project "%s" already cloned.' % project)
        return
    urls = {
        'librep': 'git://git.tuxfamily.org/gitroot/librep/main.git',
        'rep-gtk': 'git://git.tuxfamily.org/gitroot/librep/gtk.git',
        'sawfish': 'git://git.tuxfamily.org/gitroot/sawfish/main.git',
        }
    local('git clone %s %s' % (urls[project],project))
    return

def patch(project):
    'Apply local patch if there is one'
    if not os.path.exists('%s.patch'%project):
        print ('No patch file for project "%s"' % project)
        return
    with lcd(project):
        local('patch -N -p1 < ../%s.patch || true' % project)
        local('git commit -m "Bug fix" -a')

def build_master():
    '''
    Build and install latest packages
    '''
    for project in all_projects:
        clone(project)

    rebase()

    pv = [(p,"master") for p in all_projects]

    for project,version in pv:
        checkout_branch(project,version)

    for project in all_projects:
        patch(project)

    for project in all_projects:
        clean(project)

    for project,version in pv:
        build(project)
        install(project,version)

    for p,v in pv:
        print ('Built "%s" version %s' % (p,v))
    

def build_latest():
    '''
    Build and install latest packages
    '''
    for project in all_projects:
        clone(project)

    rebase()

    pv = []
    for project in all_projects:
        pv.append((project,latest(project)))

    for project,version in pv:
        checkout(project,version)

    for project in all_projects:
        patch(project)

    for project in all_projects:
        clean(project)

    for project,version in pv:
        build(project)
        install(project,version)

    for p,v in pv:
        print ('Built "%s" version %s' % (p,v))

def xephyr_test(display='1'):
    bg = ' > /dev/null 2>&1 < /dev/null &'
    local('Xephyr -geometry 800x600 :' + display + bg)
    local('sleep 1 && sawfish --display :' + display + bg)
    local('sleep 1 && xterm -display :' + display + bg)
