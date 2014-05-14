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
        if _run(cmd, cwd=self.localpath) != 0:
            raise Exception(''.join(['Failed to checkout branch ', branch, '@', self.localpath]))

    def new_branch(self, name):
        cmd = ['git', 'checkout', '-b', name]
        if _run(cmd, cwd=self.localpath) != 0:
            raise Exception(''.join(['Failed to checkout branch ', name, '@', self.localpath]))

    def fetch(self, url, ref):
        cmd = ['git', 'fetch', url, ref]
        if _run(cmd, cwd=self.localpath) != 0:
            raise Exception(''.join(['Failed to fetch ref ', ref, '@', url]))

    def delete_branch(self, branchname):
        if branchname == self.current_branch():
            raise Exception('Cannot delete branch %s because you are currently on that branch' % branchname)
        cmd = ['git', 'branch', '-D', branchname]
        if _run(cmd, cwd=self.localpath) != 0:
            raise Exception(''.join(['Failed to delete branch ', branchname, '@', self.localpath]))

    def current_branch(self):
        '''
        Returns the current branch name (if on a branch)

        I'm not actually sure what will happen if we're not on a branch and this
        is called.
        '''
        cmd = ['git', 'symbolic-ref', '--short', 'HEAD']
        proc = subprocess.Popen(cmd, cwd=self.localpath, stdout=subprocess.PIPE)
        out, err = proc.communicate()
        if err is not None:
            raise Exception('Failed to get current branch with error %s' % str(err))
        return out.strip()

    def clone(self, url, cwd=None):
        cmd = ['git', 'clone', url]
        if cwd is not None:
            cmd.append(cwd)
        if _run(cmd, cwd=self.localpath) != 0:
            raise Exception(''.join(['Failed to clone repo ', url]))

    def is_repo(self):
        cmd = ['git', 'status']
        return 0 == _run(cmd, cwd=self.localpath)

    def init_repo(self):
        if not self.is_repo():
            cmd = ['git', 'init']
            if _run(cmd, cwd=self.localpath) != 0:
                raise Exception('Failed to init repo @ %s' % self.localpath)
