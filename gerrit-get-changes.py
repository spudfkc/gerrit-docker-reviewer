#!/usr/bin/env python

##############################################################################
###
###
##############################################################################

import urllib2
import json
import subprocess
import zipfile

import random
import string

from shutil import copyfile as cp


##############################################################################
### GLOBALS
##############################################################################

DOCKERFILE_DIR = '.'
config = None
CONFIG_FILE = 'config'

##############################################################################

def loadConfigFile(filename):
    global config
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
    except IOError:
        print(''.join(['ERROR: could not find config file: ', filename]))
        exit(2)

def randstring(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

##############################################################################
def _run(cmd):
    proc = subprocess.Popen(cmd)
    #TODO

class GitRepo:
    currentbranch = None

    def __init__(self, localpath, url):
        self.path = path

    def checkout(self, branch):
        cmd = ['git', 'checkout', branch]
        return _run(cmd)

    def fetch(self, url, ref):
        cmd = ['git', 'fetch', url, ref]
        return _run(cmd)

class Docker:
    def __init__(self):
        pass

    def build(self, path):
        pass

    def run(self, cmd):
        pass

class Builder:
    def __init__(self):
        pass

    def build(self):
        pass

    def publish(self):
        pass


def getReviews():
    url = config.get('baseUrl') + 'changes/?q=status:open+reviewer:self&o=CURRENT_REVISION'
#    print 'url= ' + url
    ### set up http/auth stuff
    passwdMan = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwdMan.add_password(None, url, config.get('username'),
            config.get('apiPasswd'))

    authHandler = urllib2.HTTPDigestAuthHandler(passwdMan)

    opener = urllib2.build_opener(authHandler)
    urllib2.install_opener(opener)

    pagehandle = urllib2.urlopen(url)
    # cut off first 4 chars because they are not valid json
    body = pagehandle.read()[4:]
#    print body
    j = json.loads(body)
    return j


def checkoutChange(localProject, selectedChange, currentRev):
    gitUrl = selectedChange['revisions'][currentRev]['fetch']['ssh']['url']
    gitRef = selectedChange['revisions'][currentRev]['fetch']['ssh']['ref']

    # FIXME no hardcoded index, should be after protocol
    urlParts = [gitUrl[:6], config['username'], '@', gitUrl[6:]]

    gitUrl = ''.join(urlParts)
    gitCmd = ['git', 'fetch', gitUrl, gitRef]
    print ' '.join(gitCmd)

    ### git fetch
    try:
        localProject = config['repos'].get(project, project[project.rindex('/'):])
    except ValueError:
        pass
    print 'INFO: project is ' + localProject


    gitProc = subprocess.Popen(gitCmd, cwd=config['workspace']+'/'+localProject)
    gitProc.wait()
    if gitProc.returncode != 0:
        raise Exception('Failed git fetch')

    ### git checkout 
    gitCmd = ['git', 'checkout', 'FETCH_HEAD']
    gitProc = subprocess.Popen(gitCmd, cwd=config['workspace']+'/'+localProject)
    gitProc.wait()
    if gitProc.returncode != 0:
        raise Exception('Failed git checkout')

    # FIXME clean up branch!
    newBranchName = selectedChange['change_id'] + randstring(16)
    gitCmd = ['git', 'checkout', '-b', newBranchName]
    gitProc = subprocess.Popen(gitCmd,
            cwd=config['workspace']+'/'+localProject)
    gitProc.wait()
    if gitProc.returncode != 0:
        raise Exception('Failed to switch to new branch')

    return newBranchName


def publishChange(localProject):
    pubCmd = ['ant', 'publish']
    pubProc = subprocess.Popen(pubCmd, cwd=config['workspace']+'/'+localProject)
    pubProc.wait()
    if pubProc.returncode != 0:
        raise Exception('Failed to publish change in project %s' % localProject)


def buildUCD(dir):
    buildCmd = ['ant', 'clean', 'dist']
    buildProc = subprocess.Popen(buildCmd,
            cwd=config['workspace']+'/'+config['repos']['urban-deploy'])
    buildProc.wait()
    if buildProc.returncode != 0:
        raise Exception('Failed ant build')


def startUCDContainer(dir):
    # unzip install zip
    dist = [dir, '/', 'dist/install/', 'ibm-ucd-dev.zip']
    z = zipfile.ZipFile(''.join(dist))
    z.extractall(''.join(dist[:len(dist)-1]))

    # copy install.properties for non-interactive install
    dest = [dir, '/dist/install/ibm-ucd-install/install.properties']
    cp('install.properties', ''.join(dest))

    # build docker image from dockerfile
    dockerBuildCmd = ['docker', 'build', DOCKERFILE_DIR]
    dbuildProc = subprocess.Popen(dockerBuildCmd, stdout=subprocess.PIPE)
    out, err = dbuildProc.communicate()
    successMsg = 'Successfully built'
    successFound = out.rindex(successMsg)
    if successFound < 0:
        raise Exception('Docker image failed to build')

    # parse the docker image id
    imageId = out[successFound - len(successMsg):].strip()
    # run docker image - this path is determined by install.properties
    # the directory arg is determined by the install.properties file
    # TODO should probably pull this in from there somehow?
    dockerRunCmd = ['docker', 'run', '-P', imageId,
            '/opt/udeploy/servers/1/bin/server', 'run']

    drunProc = subprocess.Popen(dockerRunCmd)
    return imageId

def displayReviews(reviews):
    for i, review in enumerate(reviews):
        line = [' (', str(i), ') ', review.get('subject'),
                review.get('owner').get('name')]
        print(''.join(line))

def getChange(reviews):
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
    loadConfigFile(CONFIG_FILE)
    reviews = getReviews()
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

    branch = checkoutChange(localProject, selectedChange, currentRev)

    if project != 'urban-deploy':
        publishChange(localProject)

    ucdDir = ''.join([config.get('workspace'), '/',
            config.get('repos').get('urban-deploy')])

    buildUCD(ucdDir)
    imageId = startUCDContainer(ucdDir)
    # FIXME seperate buildDockerIMage and start/run docker image

    # TODO cleanup git branch (shoudl have changeId as branch name)
    # apply to each affected repo
    # should save original branch and check that back out when finished

    ### get docker ip/port
    dockerPsCmd = ['docker', 'ps']
    dpsProc = subprocess.Popen(dockerPsCmd, stdout=subprocess.PIPE)
    out, err = dpsProc.communicate()

    # TODO make pretty output
    print 'DOCKER OUTPUT:\n'+out


if __name__ == '__main__':
    main()
