class Builder:
    def __init__(self, dir):
        self.dir = dir

    @abstractmethod
    def build(self):
        pass
