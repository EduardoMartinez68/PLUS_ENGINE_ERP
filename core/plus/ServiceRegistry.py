class ServiceRegistry:
    #here function is for save the functions of the business logic and can get from a plugin for run the service
    _services = {}

    @classmethod
    def register(cls, name, func):
        cls._services[name] = func

    @classmethod
    def get(cls, name):
        return cls._services[name]