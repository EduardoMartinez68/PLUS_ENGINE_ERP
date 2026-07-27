from functools import wraps
from django.http import JsonResponse
from core.Plus import Plus

def require_permission(permission_code):
    """
    Decorator to check if the user has a specific permission.
    If they don't, it returns a standardized JSON response.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1. We searched for the user among the received arguments.
            user = None
            
            # If the second argument is directly the user (as in cls, user, data)
            if len(args) > 1 and hasattr(args[1], 'is_authenticated'):
                user = args[1]
            # if the  el argument have request.user (this only if is a view like in django)
            elif len(args) > 0 and hasattr(args[0], 'user'):
                user = args[0].user
            elif len(args) > 1 and hasattr(args[1], 'user'):
                user = args[1].user

            # 2. We validate the permit
            if not user or not Plus.this_user_have_this_permission(user, permission_code):
                return JsonResponse(
                    {
                        "success": False, 
                        "answer": "message.this-user-not-have-this-permission", 
                        "error": "this user not have this permission"
                    },
                    status=200
                )

            # 3. If everything is in order, we run the service
            return func(*args, **kwargs)
        return wrapper
    return decorator