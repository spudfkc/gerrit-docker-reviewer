import subprocess
from util import runcmd as _run

'''
This is basic wrapper around Docker.

It is used to interact with docker via command line.
'''

def build(dockerfilepath='.'):
    '''
    Builds the Dockerfile at the specified path and returns the image ID.

    Raises an Exception if the image does not successfully build.
    '''
    cmd = ['docker', 'build', dockerfilepath]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = proc.communicate()

    successmsg = 'Successfully built '
    successfound = -1
    try:
        imageid = out[out.rindex(successmsg) + len(successmsg):]
    except ValueError:
        raise Exception('Dockerfile build failed')

    try:
        tag = imageid.index('(')
        if tag >= 0:
            imageid = imageid[:tag]
    except ValueError:
        pass # no tag - continue

    try:
        # let's look for '\nRemoving'...
        nl = imageid.index('\n')
        imageid = imageid[:nl]
    except ValueError:
        pass #
    return imageid.strip()

def run(image, cmd=None, daemon=False, exposeports=True):
    '''
    Equivalent to `docker run` but a bit simplified
    '''
    basecmd = ['docker', 'run', image]
    if cmd is None:
        # TODO add default args to `docker run`
        pass
    else:
        basecmd.extend(cmd)

    if exposeports:
        basecmd.insert(2, '-P')

    if daemon:
        basecmd.insert(2, '-d')

    # TODO add expose ports functionality

    if _run(basecmd) != 0:
        raise Exception('Failed `%s`' % str(basecmd))

def ps():
    cmd = ['docker', 'ps']
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    if err is not None:
        raise Exception('Failed `docker ps`')
    return out

def get_mapped_ports():
    psout = ps()
    result = psout[psout.find('0.0.0.0'):]
    result = result[:result.find('    ')]
    return result.split(',')
