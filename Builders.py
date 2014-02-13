import zipfile

from util import runcmd as run
from shutil import copyfile as copy

class Builder:
    def __init__(self, dir):
        self.dir = dir

class UCDBuilder:
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

    def post_build(self):
        # extract the install zip
        distzip = 'ibm-ucd-dev.zip'
        dist = [self.dir, '/dist/install/', distzip]
        z = zipfile.ZipFile(''.join(dist))
        z.extractall(''.join(dist[:len(dist)-1]))

        # copy install.properties for non-interactive install
        extractdir = '/dist/install/ibm-ucd-install/'
        installprops = 'install.properties'
        dest = [self.dir, extractdir, installprops]
        copy(installprops, ''.join(dest))


class AntBuilder:
    def __init__(self, dir):
        pass
