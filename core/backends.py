from django.contrib.auth.backends import BaseBackend
from core.models import CustomUser, sha256_hex


class EmailHashBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        # Iterar sobre todos los usuarios porque el email está encriptado
        for user in CustomUser.objects.all():
            if user.email == username and user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
        
    