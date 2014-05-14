from abc import abstractmethod


class Builder:
    def __init__(self, dir):
        self.dir = dir

    @abstractmethod
    def prebuild(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @abstractmethod
    def postbuild(self):
        pass
