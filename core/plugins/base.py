from abc import ABC, abstractmethod

class BasePlugin(ABC):
    name = "BasePlugin"

    def is_active(self, request=None):
        return True

    def is_valid(self, request=None, data=None):
        return True

    @abstractmethod
    def execute(self, **kwargs):
        pass