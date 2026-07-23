class Context:

    def __init__(self, **kwargs):

        self.__dict__.update(kwargs)

        self.result = None