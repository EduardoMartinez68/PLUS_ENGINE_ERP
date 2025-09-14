from django.contrib.auth.backends import BaseBackend
from core.models import CustomUser, sha256_hex


class EmailHashBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        try:
            email_hashed = sha256_hex(username)  # hash del email
            user = CustomUser.objects.get(email_hash=email_hashed)
            if user.check_password(password):
                return user
        except CustomUser.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None