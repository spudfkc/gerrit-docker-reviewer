#!/usr/bin/env python

##############################################################################
###
###
##############################################################################

import urllib2
import json
import sys

from Gerrit import Gerrit
from Builders import UCDBuilder
from Git import Git
from Docker import UCDDocker
import util
from util import runcmd as _run
from shutil import rmtree as rmdir

##############################################################################
### GLOBALS
##############################################################################

DOCKERFILE_DIR = '.'
config = None
CONFIG_FILE = 'config'

##############################################################################

def checkoutChange(localProject, selectedChange, currentRev):
    '''
    A function that does too much.
    '''
    project = selectedChange.get('project')
    gitUrl = selectedChange['revisions'][currentRev]['fetch']['ssh']['url']
    gitRef = selectedChange['revisions'][currentRev]['fetch']['ssh']['ref']

    # FIXME no hardcoded index, should be after protocol
    urlParts = [gitUrl[:6], config['username'], '@', gitUrl[6:]]

    gitUrl = ''.join(urlParts)

    localProject = None
    try:
        localProject = config.get('repos').get(project)
    except ValueError:
        raise Exception('Project %s not found in config file' % project)
    print('INFO: project is ' + str(localProject))

    projectDir = ''.join([config.get('workspace'), '/', localProject])

    git = Git(projectDir)
    builder = UCDBuilder(projectDir)

    originalbranch = git.current_branch()

    git.fetch(gitUrl, gitRef)

    git.checkout('FETCH_HEAD')
    newbranch = selectedChange.get('change_id') + '/' + util.randstring(8)
    git.new_branch(newbranch)

    ucdDir = projectDir
    ucdBuilder = builder
    ucdGit = None
    if project != 'urban-deploy':
        ucdDir = ''.join([config.get('workspace'), '/',
            config.get('repos').get('urban-deploy')])
        ucdBuilder = UCDBuilder(ucdDir)
        builder.publish()

    # Build UCD
    ucdBuilder.pre_build()
    ucdBuilder.build()
    ucdBuilder.post_build()

    # restore original branch
    git.checkout(originalbranch)


def displayReviews(reviews):
    '''
    Displays the given reviews in the terminal.

    Each review is indexed, starting at 1.

    Format:
    (i) subject owner
    '''
    for i, review in enumerate(reviews):
        line = [' (', str(i+1), ') ', review.get('subject'), '-',
                review.get('owner').get('name')]
        print(' '.join(line))


def getChange(reviews):
    '''
    Prompts the user to select a change to review given a list of reviews
    This returns the selected change.
    '''
    selected = False
    changeindex = -1
    while not selected:
        try:
            changeindex = int(raw_input())
            if changeindex > 0 and changeindex <= len(reviews):
                changeindex -= 1
                selected = True
        except ValueError:
            pass # ignore non-numeric input
    return reviews[changeindex]


def main():
    # parse arguments
    onlyDeploy = False
    daemonMode = False
    if len(sys.argv) > 1:
        if '-D' in sys.argv:
            onlyDeploy = True
        if '-d' in sys.argv:
            daemonMode = True

    # load config
    global config
    config = util.loadConfigFile(CONFIG_FILE)

    if not onlyDeploy:
        gerrit = Gerrit(config.get('baseUrl'), config.get('username'),
            config.get('apiPasswd'))
        reviews = gerrit.get_open_reviews()
        if not len(reviews) > 0:
            print('No open reviews')
            exit(0)
        displayReviews(reviews)
        selectedChange = getChange(reviews)

        project = selectedChange.get('project')
        currentRev = selectedChange.get('current_revision')

        try:
            localProject = config.get('repos').get('project')
        except KeyError:
            print('ERROR: could not find project %s in config file' % project)
            exit(1)

        print('INFO: project is %s' % project)

        checkoutChange(localProject, selectedChange, currentRev)

    docker = UCDDocker(''.join([config.get('workspace'), '/',
        config.get('repos').get('urban-deploy')]))
    docker.pre_build()
    image = docker.build(DOCKERFILE_DIR)
    runprocess = docker.run(image)

    print('done.')


##############################################################################


if __name__ == '__main__':
    main()
