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


DOCKERFILE_DIR = '.'


config = None
with open('config', 'r') as f:
    config = json.load(f)

if config is None:
    exit(2)

def randstring(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

def getReviews():
    url = config['baseUrl'] + 'changes/?q=status:open+reviewer:self&o=CURRENT_REVISION'
#    print 'url= ' + url
    ### set up http/auth stuff
    passwdMan = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwdMan.add_password(None, url, config['username'], config['apiPasswd'])

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





j = getReviews()

### build git cmd
i = 1
for review in j:
    line = [' (', str(i), ')  ', review['subject'], review['owner']['name']]
    print ''.join(line)
    i += 1

### have the user pick a change to use
selected = False
changeNum = -1
while not selected:
    try:
        changeNum = int(raw_input())
        if changeNum > 0 and changeNum <= len(j):
            changeNum -= 1
            selected = True
    except ValueError:
        pass

### build the git command
selectedChange = j[changeNum]
# get the latest revision
project = selectedChange['project']
currentRev = selectedChange['current_revision']

### git fetch
try:
    localProject = config['repos'][project]
except KeyError:
    print('ERROR: Could not find project %s in config file' % project)
    exit(1)
#localProject = config['repos'].get(project, project[project.rindex('/'):])
print('INFO: project is ' + localProject)

branch = checkoutChange(localProject, selectedChange, currentRev)

if project != 'urban-deploy':
    publishChange(localProject)

ucdDir = config['workspace']+'/'+config['repos']['urban-deploy']
buildUCD(ucdDir)
imageId = startUCDContainer(ucdDir)


# FIXME this doesn't work as intended
# clean up git branch
# TODO save old branch and check that one back out
#coBranchCmd = ['git', 'checkout', 'master']
#subprocess.Popen(coBranchCmd, cwd=config['workspace']+'/'+localProject)
#
#delBranchCmd = ['git', 'branch', '-D', branch]
#delBranchProc = subprocess.Popen(delBranchCmd,
#        cwd=config['workspace']+'/'+localProject)
#delBranchProc.wait()
#if delBranchProc.returncode != 0:
#    print('WARN: Unable to clean up git branch %(br)s in project %(pr)s' %
#            {"br": branch, "pr": localProject})


### get docker ip/port
dockerPsCmd = ['docker', 'ps']
dpsProc = subprocess.Popen(dockerPsCmd, stdout=subprocess.PIPE)
out, err = dpsProc.communicate()

# TODO make pretty output
print 'DOCKER OUTPUT:\n'+out
