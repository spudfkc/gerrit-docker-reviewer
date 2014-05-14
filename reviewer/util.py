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
        print str(x)
        if x.errno == errno.ENOTDIR:
            copyfile(src, dest)
        else: raise


def loadConfigFile(filename):
    '''
    Loads a file into a JSON object/dict.

    The file should be valid JSON using double-quotes.

    Raises an Exception if the file could not be read
    '''
    config = None
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
    except IOError:
#        print(''.join(['ERROR: could not find config file: ', filename]))
        exit(2)
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

    Will raise an Exception if the command had a non-zero exit code.
    '''
    print('DEBUG: running cmd: ' + ' '.join(cmd) + ' @ ' + cwd)
    proc = subprocess.Popen(cmd, cwd=cwd)
    proc.wait()
    return proc.returncode
