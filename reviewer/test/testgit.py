import unittest
from .. import Git
from shutil import rmtree
from os import makedirs
from os.path import exists

class GitTests(unittest.TestCase):

    test_git_dir = '/tmp/gittest'

    def setUp(self):
        self.cleanup()
        self.git = Git.Git(self.test_git_dir)
        self.assertFalse(self.git.is_repo())

    def testClone(self):
        self.git.clone('https://github.com/spudfkc/shibescraper.git', cwd='.')
        self.assertTrue(self.git.is_repo())

    def testCheckout(self):
        self.git.init_repo()
        self.assertEquals(self.git.current_branch(), 'master')
        self.git.new_branch('testbranch')
        self.assertEquals(self.git.current_branch(), 'testbranch')
        self.git.checkout('master')
        self.assertEquals(self.git.current_branch(), 'master')

    def testNewBranch(self):
        self.git.init_repo()
        self.git.new_branch('testbranch')
        self.assertEquals(self.git.current_branch(), 'testbranch')

    def testDeleteBranch(self):
        # TODO
        pass

    def testCurrentBranch(self):
        self.git.init_repo()
        self.assertEquals(self.git.current_branch(), 'master')

    def testIsRepo(self):
        self.assertFalse(self.git.is_repo())
        self.git.init_repo()
        self.assertTrue(self.git.is_repo())

    def testInitRepo(self):
        self.git.init_repo()
        self.assertTrue(self.git.is_repo())

    def cleanup(self):
        if exists(self.test_git_dir):
            rmtree(self.test_git_dir)
        self.assertFalse(exists(self.test_git_dir))
        makedirs(self.test_git_dir)
        self.assertTrue(exists(self.test_git_dir))


def main():
    unittest.main()

if __name__ == '__main__':
    main()
