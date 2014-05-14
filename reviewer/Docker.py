import subprocess
from util import runcmd as _run

class Docker:
    '''
    This is basic wrapper around Docker.

    It is used to interact with docker via command line.
    '''
    def __init__(self):
        pass

    def build(self, dockerfilepath='.'):
        '''
        Builds the Dockerfile at the specified path and returns the image ID.

        Raises an Exception if the image does not successfully build.
        '''
        cmd = ['docker', 'build', dockerfilepath]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = proc.communicate()

        successmsg = 'Successfully built'
        successfound = -1
        try:
            successfound = out.rindex(successmsg)
        except ValueError:
            pass
        if successfound < 0:
            raise Exception('Dockerfile build failed')

        imageid = out[successfound + len(successmsg):]
        try:
            tag = imageid.index('(')
            if tag >= 0:
                imageid = imageid[:tag]
        except ValueError:
            pass
        return imageid.strip()

    def run(self, image, daemon=False, cmd=None, exposeports=None):
        '''
        Equivalent to `docker run` but a bit simplified
        '''
        basecmd = ['docker', 'run', image]
        if cmd is None:
            # TODO add default args to `docker run`
            pass
        else:
            basecmd.extend(cmd)

        if daemon:
            basecmd.insert(2, '-d')

        # TODO add expose ports functionality

        if _run(basecmd) != 0:
            raise Exception('Failed `docker run`')

    def ps(self):
        cmd = ['docker', 'ps']
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err is not None:
            raise Exception('Failed `docker ps`')
        return out

    def get_mapped_ports(self):
        psout = self.ps()
        result = psout[psout.find('0.0.0.0'):]
        result = result[:result.find('    ')]
        return result.split(',')
