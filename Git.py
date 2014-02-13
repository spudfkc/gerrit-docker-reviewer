import subprocess

from util import runcmd as _run


class Git:
    '''
    This class represents a Git repository

    It has several functions to do stuff with the repo, such as creating a new
    branch, fetching, checking out a different branch, getting the current
    branch.
    '''
    localpath = None

    def __init__(self, localpath):
        self.localpath = localpath

    def checkout(self, branch):
        cmd = ['git', 'checkout', branch]
        return _run(cmd, cwd=self.localpath)

    def new_branch(self, name):
        cmd = ['git', 'checkout', '-b', name]
        return _run(cmd, cwd=self.localpath)

    def fetch(self, url, ref):
        cmd = ['git', 'fetch', url, ref]
        return _run(cmd, cwd=self.localpath)

    def current_branch(self):
        '''
        Returns the current branch name (if on a branch)

        I'm not actually sure what will happen if we're not on a branch and this
        is called.
        '''
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        proc = subprocess.Popen(cmd, cwd=self.localpath, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        return out.strip()

