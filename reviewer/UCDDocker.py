import os
from util import copy as copy
from reviewer.Docker import Docker

class UCDDocker(Docker):
    '''
    Contains UCD specific instructions for pre/post building of Dockerfile
    '''

    installdir = 'ibm-ucd-install'

    def __init__(self, ucddir, ucdversion=6):
        self.ucddir = ucddir
        if ucdversion < 6:
            self.installdir = 'udeploy-install'

    def pre_build(self):
        src = ''.join([self.ucddir, '/dist/install/', self.installdir])
        if os.path.exists(src):
            rmtree(src)

        dest = 'ibm-icd-install'
        # copy the built directory into the current directory
        copy(src, dest)
