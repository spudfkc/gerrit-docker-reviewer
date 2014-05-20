#!/usr/bin/env python

import urllib2, json, sys, os, imp
import reviewer.Docker as docker
import reviewer.util as util

from reviewer import util
from reviewer.Gerrit import Gerrit
from reviewer.Git import Git
from shutil import rmtree

##############################################################################
### GLOBALS
##############################################################################

config = None

##############################################################################

def build_change(project):
    '''
    Builds the given project
    '''
    builder = get_builder(project)
    builder.prebuild()
    builder.build()
    builder.postbuild()


def checkout_change(project, change, revision):
    '''
    Fetch change/rev from Gerrit, checkout in local project repo.
    '''
    # create Git obj for the project's git repo
    print '[DEBUG] sshinfo: %s ' % str(change)
    projectdir = ''.join([config.get('workspace'), '/', project])
    git = Git(projectdir)
    originalbranch = git.current_branch()
    # generate a new branch name from the change and random string
    newbranch = ''.join([change.get('change_id'), '/', util.randstring(8)])

    try:
        # get necessary info from json returned from gerrit
        sshinfo = change.get('revisions').get(revision).get('fetch').get('ssh')
        giturl = sshinfo.get('url')
        gitref = sshinfo.get('ref')

        # insert username into url
        urlparts = [giturl[:6], config.get('gerrit-username'), '@', giturl[6:]]
        giturl = ''.join(urlparts)

        git.fetch(giturl, gitref)  # fetch branch from gerrit
        git.checkout('FETCH_HEAD') # checkout fetched changes (no-branch)
        git.new_branch(newbranch)  # create a new branch for these changes

        build_change(project)
    finally:
        if git.current_branch() == newbranch:
            git.checkout(originalbranch)
            git.delete_branch(newbranch)


def get_change(reviews):
    '''
    Prompts the user to select a change for review. Returns selected change.
    '''
    validselection = False
    changeindex = -1
    while not validselection:
        try:
            changeindex = int(raw_input())
            if changeindex > 0 and changeindex <= len(reviews):
                changeindex -= 1
                validselection = True
        except ValueError:
            pass # ignore bad input - usually non-numeric
    return reviews[changeindex]


def display_reviews(reviews):
    '''
    Displays the given reviews to stdout, each review numbered (1 indexed
    '''
    for i, review in enumerate(reviews):
        line = [' (', str(i+1), ') ', review.get('subject'), '-', review.get('owner').get('name')]
        print(' '.join(line))


# FIXME maybe pass in (args*, kargs**)
def get_builder(project):
    '''
    Dynamically loads a builder for the given project.

    The builder should either be specified for the project (not yet implemented)
    Otherwise the default-builder is used.
    '''
    try:
        buildername = config.get('repos').get(project).get('builder')
    except AttributeError:
        print('[INFO] no builder found for project %s, using default' % project)
        buildername = config.get('default-builder')
    buildermod = imp.load_source(buildername, ''.join(['./reviewer/plugins/', buildername, '.py']))

    projectdir = ''.join([config.get('workspace'), '/', config.get('repos').get(project)])
    # FIXME verify that the buildermod has a load() method
    builder = buildermod.load(projectdir)
    return builder


def is_dep(projectname):
    '''
    Returns True if a given project is considered a dependency project. False otherwise
    A dependency project is a library project that is not a deployable application on its own.
    '''
    return projectname == config.get('default-project')


def display_help():
    print(
        '''
        Usage: reviewer.py [-d] [-D] [--no-build]

            -d|--daemon           Starts the Docker container as a daemon.
            -D|--deploy-only      Skips any Gerrit/Git operations and deploys
                                  your current UCD directory to a container.
            --no-build            Skips building the project
            -h|--help             Displays this text.
        ''')


def main():
    CONFIG_FILE = 'conf/nameless.config'
    # parse arguments
    onlyDeploy = False
    daemonMode = False
    doBuild = True
    if len(sys.argv) > 0:
        if '-D' in sys.argv or '--deploy-only' in sys.argv:
            onlyDeploy = True
        if '-d' in sys.argv or '--daemon' in sys.argv:
            daemonMode = True
        if '--no-build' in sys.argv:
            doBuild = False
        # TODO add project option
        if '-h' in sys.argv or '--help' in sys.argv:
            display_help()
            return

    # load config
    global config
    config = util.loadConfigFile(CONFIG_FILE)

    mainproject = None
    depproject = None

    # Use the default project if we're just deploying.
    # We may want to change this later in case we want to be able to pick
    # a project to deploy at runtime.
    mainproject = config.get('default-project')

    if not onlyDeploy:
        # Here we query Gerrit for a list of our open changes, prompt the user
        # for a change they want to build/deploy, and then do that.
        gerrit = Gerrit(config.get('gerrit-url'), config.get('gerrit-username'),
            config.get('gerrit-api-password'))

        reviews = gerrit.get_open_reviews()
        if len(reviews) < 1:
            print('Found no open reviews')
            return 0

        display_reviews(reviews)
        selectedchange = get_change(reviews)

        depproject = selectedchange.get('project')
        currentrev = selectedchange.get('current_revision')

        try:
            localproject = config.get('repos').get(depproject)
        except KeyError:
            print('[ERROR] Could not find project %s in config' % depproject)
            return 1

        print('[INFO] project is %s' % depproject)

        checkout_change(depproject, selectedchange, currentrev)

    # build the project
    if doBuild:
        build_change(mainproject)

    # build a new docker image with our Dockerfile
    imageid = docker.build()

    # start up the new docker image
    cmd = ['run']
    if daemonMode:
        cmd = ['start']
    docker.run(imageid, cmd=cmd, daemon=daemonMode)

    print "done"
    exit(0)


##############################################################################


if __name__ == '__main__':
    main()
