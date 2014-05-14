import zipfile

from reviewer.Builder import Builder as rBuilder
from reviewer.util import runcmd as _run
from shutil import copyfile as copy

def load(dir, ver=6):
    return UCDBuilder(dir, ver)

class UCDBuilder(rBuilder):
    distname = 'ibm-ucd'
    minorver = 'dev'

    def __init__(self, dir, ver=6):
        super(dir)
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
        # extract the install zip
        dist = [self.dir, '/dist/install/', self.distzip, self.minorver]
        print('DEBUG - zipfile: ' + ''.join(dist))
        z = zipfile.ZipFile(''.join(dist))
        print('DEBUG - extractall: ' + ''.join(dist[:len(dist)-2]))
        z.extractall()

        # copy install.properties for non-interactive install
        installprops = 'install.properties'
        copy(installprops, '/'.join([self.distname, '-install', installprops]))

        # TODO copy JDBC driver(s) for database type
