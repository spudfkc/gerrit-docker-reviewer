import unittest
from reviewer.Docker import Docker

class DockerTests(unittest.TestCase):

    test_image = 'spudfkc/java7'

    def setUp(self):
        self.docker = Docker()

    def test_build(self):
        pass
        #dockerfile = '.'
        #imageid = self.docker.build(dockerfile)
        #self.assertNotEquals(imageid, None)

    def test_run(self):
        image = 'ubuntu'
        self.docker.run(image)

    def test_run_with_daemon(self):
        pass

    def test_run_with_cmd(self):
        pass

    def test_ps(self):
        pass

    def test_get_mapped_ports(self):
        pass

    def tearDown(self):
        pass


def main():
    unittest.main()

if __name__ == '__main__':
    main()
