from django.http import JsonResponse

class ServiceRegistry:
    #here function is for save the functions of the business logic and can get from a plugin for run the service
    _services = {}

    @classmethod
    def register(cls, name):
        """Decorator for registering class functions or methods."""
        def decorator(func):
            cls._services[name] = func
            return func
        return decorator

    @classmethod
    def get(cls, name):
        return cls._services[name]

    @classmethod
    def execute(cls, name, *args, **kwargs):
        """
        Search for and execute a registered service.
        If it doesn't exist, return a standardized error response.
        """
        service_func = cls.get(name)

        if not service_func:
            return JsonResponse({
                "success": False,
                "answer": "message.service-not-found",
                "error": f'The service "{name}" not exist in <ServiceRegistry>'
            }, status=500)

        #Execute the function by passing it exactly the parameters received.
        return service_func(*args, **kwargs)
