import os

from reviewer.util import copy
from reviewer.Docker import Docker as rDocker

def load(dir, ver=6):
    return UCDDocker(dir, ver)

class UCDDocker(rDocker):
    '''
    Contains UCD specific instructions for pre/post building of Dockerfile
    '''

    distname = 'ibm-ucd'

    def __init__(self, ucddir, ver=6):
        self.ucddir = ucddir
        if ver < 6:
            self.distname = 'udeploy'

    def pre_build(self):
        src = ''.join([self.ucddir, '/dist/install/', self.distname, '-install'])
        if os.path.exists(src):
            rmtree(src)

        dest = 'ibm-ucd-install'
        # Copy the built directory into the current directory.
        # We need to do this because Docker doesn't like us adding files outside
        # of Docker's build directory (where we build the Dockerfile)
        copy(src, dest)
