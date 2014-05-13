import Builder
import zipfile

from util import runcmd as run
from shutil import copyfile as copy


class UCDBuilder(Builder):
    majorver = 6
    distzip = 'ibm-ucd-dev.zip'

    def __init__(self, dir):
        self.dir = dir

    def build(self):
        cmd = ['ant', 'dist', '-Ddojo.build.no=1']
        return run(cmd, cwd=self.dir)

    def publish(self):
        cmd = ['ant', 'publish']
        return run(cmd, cwd=self.dir)

    def pre_build(self):
        cmd = ['ant', 'clean-all']
        return run(cmd, cwd=self.dir)

    def update_major_version(self, ver):
        if ver == 6:
            self.majorver = 6
            self.distzip = 'ibm-ucd-dev.zip'
        else:
            self.majorver = ver
            self.distzip = 'udeploy-install.zip'

    def post_build(self):
        # extract the install zip
        dist = [self.dir, '/dist/install/', self.distzip]
        print('DEBUG - zipfile: ' + ''.join(dist))
        z = zipfile.ZipFile(''.join(dist))
        print('DEBUG - extractall: ' + ''.join(dist[:len(dist)-1]))
        z.extractall()

        # copy install.properties for non-interactive install
  #      extractdir = '/dist/install/ibm-ucd-install/'
        installprops = 'install.properties'
 #       dest = [self.dir, extractdir, installprops]
        copy(installprops, '/'.join(['ibm-ucd-install', installprops]))
#        copy(installprops, ''.join(dest))
        

