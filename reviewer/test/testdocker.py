import unittest
import reviewer.Docker as docker


class DockerTests(unittest.TestCase):

    test_image = 'spudfkc/java7'

    def setUp(self):
        pass

    def test_build(self):
        dockerfile = '.'
        imageid = docker.build(dockerfile)
        self.assertNotEquals(imageid, None)

    def test_run(self):
        image = 'spudfkc/java7'
        cmds = ['echo', 'hello']
        docker.run(image, cmd=cmds)

    def test_run_with_daemon(self):
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
