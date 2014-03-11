import subprocess
import os

from util import runcmd as _run
from util import copy as copy
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
        src = ''.join([self.ucddir, '/dist/install/ibm-ucd-install'])
        if os.path.exists(src):
            rmtree(src)

        dest = 'ibm-ucd-install'
        print('DEBUG - copy from ' + str(src) + ' to ' + str(dest))
        # copy(src, dest) # this isn't necessary? I'm actually not sure?

    def build(self, dockerfilepath):
        dockerBuildCmd = ['docker', 'build', dockerfilepath]
        dbuildProc = subprocess.Popen(dockerBuildCmd, stdout=subprocess.PIPE)
        out, err = dbuildProc.communicate()
        successMsg = 'Successfully built'
        successFound = -1
        try:
            successFound = out.rindex(successMsg)
        except ValueError:
            pass
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

    def run(self, image, daemon=False, cmd=None):
        # TODO probably should have an option to start in daemon mode (default)
        # and then maybe parse which ports the image is running on and display
        # them to user.
        if cmd is None:
            cmd = ['docker', 'run', '-P', image, 'run']
            if daemon:
                cmd.insert(2, '-d')
        _run(cmd)

    def ps(self):
        dockerPsCmd = ['docker', 'ps']
        dpsProc = subprocess.Popen(dockerPsCmd, stdout=subprocess.PIPE)
        out, err = dpsProc.communicate()
        return out

    def get_mapped_ports(self):
        psout = self.ps()
        result = psout[psout.find('0.0.0.0'):]
        result = result[:result.find('    ')]
        return result.split(',')


