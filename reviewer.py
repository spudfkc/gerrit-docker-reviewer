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


def _run(cmd, cwd='.'):
    proc = subprocess.Popen(cmd, cwd=cwd)
    proc.wait()
    if proc.returncode != 0:
        raise Exception('Command failed: ' + ' '.join(cmd))


##############################################################################


class GitRepo:
    localpath = None

    def __init__(self, localpath):
        self.localpath = localpath

    def checkout(self, branch):
        cmd = ['git', 'checkout', branch]
        return _run(cmd, cwd=self.localpath)

    def new_branch(self, name):
        cmd = ['git', 'checkout', '-b', name]
        return _run(cmd, cwd=self.localpath)

    def fetch(self, url, ref):
        cmd = ['git', 'fetch', url, ref]
        return _run(cmd, cwd=self.localpath)

    def current_branch(self):
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        proc = subprocess.Popen(cmd, cwd=self.localpath, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out


class UCDBuilder:
    dir = None

    def __init__(self, dir):
        self.dir = dir

    def build(self):
        cmd = ['ant', 'dist', '-Ddojo.build.no=1', '-Denun.no=1']
        return _run(cmd, cwd=self.dir)

    def publish(self):
        cmd = ['ant', 'publish']
        return _run(cmd, cwd=self.dir)

    def post_build(self):
        # unzip install zip
        dist = [self.dir, '/', 'dist/install/', 'ibm-ucd-dev.zip']
        z = zipfile.ZipFile(''.join(dist))
        z.extractall(''.join(dist[:len(dist)-1]))

        # copy install.properties for non-interactive install
        dest = [self.dir, '/dist/install/ibm-ucd-install/install.properties']
        cp('install.properties', ''.join(dest))

    def pre_build(self):
        cmd = ['ant', 'clean-all']
        return _run(cmd, cwd=self.dir)


class Docker:
    def __init__(self):
        pass

    def build(self, dockerfilepath):
        dockerBuildCmd = ['docker', 'build', dockerfilepath]
        dbuildProc = subprocess.Popen(dockerBuildCmd, stdout=subprocess.PIPE)
        out, err = dbuildProc.communicate()
        successMsg = 'Successfully built'
        successFound = out.rindex(successMsg)
        if successFound < 0:
            raise Exception('Docker image failed to build')

        imageId = out[successFound - len(successMsg):].strip()
        return imageId


    # FIXME this is awful
    def run(self, image, cmd):
        # run docker image - this path is determined by install.properties
        # the directory arg is determined by the install.properties file
        # TODO should probably pull this in from there somehow?
        dockerRunCmd = ['docker', 'run', '-P', imageId,
                '/opt/udeploy/servers/1/bin/server', 'run']

        return subprocess.Popen(dockerRunCmd)

    def ps(self):
        dockerPsCmd = ['docker', 'ps']
        dpsProc = subprocess.Popen(dockerPsCmd, stdout=subprocess.PIPE)
        out, err = dpsProc.communicate()
        return out


##############################################################################


def getReviews():
    url = config.get('baseUrl') + 'changes/?q=status:open+reviewer:self&o=CURRENT_REVISION'
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
    j = json.loads(body)
    return j


def checkoutChange(localProject, selectedChange, currentRev):
    project = selectedChange.get('project')
    gitUrl = selectedChange['revisions'][currentRev]['fetch']['ssh']['url']
    gitRef = selectedChange['revisions'][currentRev]['fetch']['ssh']['ref']

    # FIXME no hardcoded index, should be after protocol
    urlParts = [gitUrl[:6], config['username'], '@', gitUrl[6:]]

    gitUrl = ''.join(urlParts)
    gitCmd = ['git', 'fetch', gitUrl, gitRef]
    print ' '.join(gitCmd)

    localProject = None
    try:
        localProject = config.get('repos').get(project)
    except ValueError:
        raise Exception('Project %s not found in config file' % project)
    print('INFO: project is ' + str(localProject))

    projectDir = ''.join([config.get('workspace'), '/', localProject])

    git = GitRepo(projectDir)
    builder = UCDBuilder(projectDir)

    originalbranch = git.current_branch()

    git.fetch(gitUrl, gitRef)

    git.checkout('FETCH_HEAD')
    newbranch = selectedChange.get('change_id') + '/' + randstring(8)
    git.new_branch(newbranch)

    ucdDir = projectDir
    ucdBuiler = builder
    if project == 'urban-deploy':
        ucdDir = ''.join([config.get('workspace'), '/',
            config.get('repos').get('urban-deploy')])
        ucdBuilder = UCDBuilder(ucdDir)
    else:
        builder.publish()

    # Build UCD
    ucdBuilder.pre_build()
    ucdBuilder.build()
    ucdBuilder.post_build()

    # restore original branch
    git.checkout(originalbranch)


def displayReviews(reviews):
    for i, review in enumerate(reviews):
        line = [' (', str(i+1), ') ', review.get('subject'),
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

    branch = checkoutChange(localProject, selectedChange, currentRev)
    docker = Docker()
    image = docker.build(DOCKER_FILE_DIR)
    runprocess = docker.run(image)

    print('done.')


##############################################################################


if __name__ == '__main__':
    main()
