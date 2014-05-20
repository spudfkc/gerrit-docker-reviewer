import zipfile, os

from reviewer.Builder import Builder as rBuilder
from reviewer.util import runcmd as _run
from reviewer.util import copy
from shutil import rmtree

def load(dir, ver=6):
    return UCDBuilder(dir, ver)

class UCDBuilder(rBuilder):
    distname = 'ibm-ucd'
    minorver = 'dev'

    def __init__(self, dir, ver=6):
        rBuilder.__init__(self, dir)
        if ver != 6:
            self.distname = 'udeploy'

    def build(self):
        '''
        Creates the project dist and install files, and then published to CS repo
        '''
        cmd = ['ant', 'dist', '-Ddojo.build.no=1', '-Dresolve.no=1']
        if _run(cmd, cwd=self.dir) != 0:
            raise Exception('Failed to build project')
        self.publish()

    def publish(self):
        '''
        Publishes the dist to local codestation repo

        Runs `ant publish`
        '''
        cmd = ['ant', 'publish']
        _run(cmd, cwd=self.dir)

    def prebuild(self):
        '''
        Cleans out any deps and grabs them again.

        Runs `ant clean-all resolve`
        '''
        cmd = ['ant', 'clean-all', 'resolve']
        _run(cmd, cwd=self.dir)

    def postbuild(self):
        '''
        Extracts install dist and copies over install.properties for install
        '''
        try:
            self._extract_dist()
            self._copy_install_props()
            self._copy_extracted_dist()
        except IOError:
            pass

    def _extract_dist(self):
        # extract the install zip
        dist = [self.dir, '/dist/install/', self.distname, '-', self.minorver, '.zip']
        z = zipfile.ZipFile(''.join(dist))
        z.extractall(''.join(dist[:2]))

    def _copy_install_props(self):
        # copy install.properties for non-interactive install
        # TODO edit props for install
        installprops = 'res/install.properties'
        dest = ''.join([self.dir, '/dist/install/', self.distname, '-install/install.properties'])
        copy(installprops, dest)

    def _copy_extracted_dist(self):
        # Copy the built directory into the current directory.
        # We need to do this because Docker doesn't like us adding files outside
        # of Docker's build directory (where we build the Dockerfile)
        src = ''.join([self.dir, '/dist/install/', self.distname, '-install'])
        dest = 'ibm-ucd-install'
        if os.path.exists(dest):
            rmtree(dest)
        copy(src, dest)
        # TODO copy JDBC driver(s) for database type
