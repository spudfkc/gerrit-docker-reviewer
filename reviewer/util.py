from shutil import copyfile
from shutil import copytree

import string
import random
import json
import subprocess
import errno


def copy(src, dest):
    '''
    Recursively copy a directory with files
    '''
    try:
        copytree(src, dest)
    except OSError as x:
        if x.errno == errno.ENOTDIR:
            copyfile(src, dest)
        else: raise


def loadConfigFile(filename):
    '''
    Loads a file into a JSON object/dict.

    The file should be valid JSON using double-quotes.

    Raises an IOError if the file could not be read
    '''
    config = None
    with open(filename, 'r') as f:
        config = json.load(f)
    return config


def randstring(length):
    '''
    Creates and returns a random string of lowercase letters of given length
    '''
    return ''.join(random.choice(string.lowercase) for i in range(length))


def runcmd(cmd, cwd='.'):
    '''
    Runs the given cmd in a subprocess.

    cmd should be an array of strings that make up the command to run.
    cwd should be the directory in which to trun the commands.

    Returns the process's exit code
    '''
    print('DEBUG: running cmd: ' + ' '.join(cmd) + ' @ ' + cwd)
    proc = subprocess.Popen(cmd, cwd=cwd)
    proc.wait()
    return proc.returncode
