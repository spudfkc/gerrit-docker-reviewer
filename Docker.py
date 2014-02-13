import subprocess
import os

from util import runcmd as _run
from util import copy
from shutil import rmtree

class UCDDocker:
    '''
    Wrapper class for using Docker

    Needs to be more generic, since at the moment it still is specific to UCD
    and our UCD Dockerfile
    '''
    def __init__(self, ucddir):
        self.ucddir = ucddir

    def pre_build(self):
        src = ''.join([ucddir, '/dist/install/ibm-ucd-install'])
        if os.path.exists(src):
            rmtree(src)

        dest = 'ibm-ucd-install'
        copy(src, dest)

    def build(self, dockerfilepath):
        dockerBuildCmd = ['docker', 'build', dockerfilepath]
        dbuildProc = subprocess.Popen(dockerBuildCmd, stdout=subprocess.PIPE)
        out, err = dbuildProc.communicate()
        successMsg = 'Successfully built'
        successFound = out.rindex(successMsg)
        if successFound < 0:
            raise Exception('Docker image failed to build')

        imageId = out[successFound + len(successMsg):]
        try:
            tag = imageId.index('(')
            if tag >= 0:
                imageId = imageId[:tag]
        except ValueError:
            pass
        return imageId.strip()

    # FIXME this is awful
    def run(self, image, cmd=None):
        # run docker image - this path is determined by install.properties
        # the directory arg is determined by the install.properties file
        # TODO should probably pull this in from there somehow?
        if cmd is None:
            cmd = ['docker', 'run', '-P', image, 'run']
        _run(cmd)

    def ps(self):
        dockerPsCmd = ['docker', 'ps']
        dpsProc = subprocess.Popen(dockerPsCmd, stdout=subprocess.PIPE)
        out, err = dpsProc.communicate()
        return out

