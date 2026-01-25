from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.sessions.models import Session
from core.models import UserSession

class SubscriptionCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Solo verificamos si el usuario está logueado y no es un administrador
        if request.user.is_authenticated and not request.user.is_staff:
            # 2. Definimos URLs que NO deben bloquearse (para evitar bucles infinitos)
            # Asegúrate de tener una URL llamada 'subscription_expired' o similar
            exempt_urls = [
                reverse('logout'),
            ]

            if request.path not in exempt_urls:
                # 3. Obtenemos la suscripción usando el related_name que definiste
                subscription = getattr(request.user, 'subscription', None)

                # 4. Verificamos si expiró o no tiene
                if not subscription or subscription.is_expired():
                    messages.error(request, "Tu suscripción ha expirado. Por favor, inicia sesión de nuevo o contacta a soporte.")

                    #here we will to delete all the sessions of the user 
                    session_key = request.session.session_key
                    if session_key:
                        # delete the connection with other drivers
                        UserSession.objects.filter(
                            user=request.user,
                            session__session_key=session_key
                        ).delete()

                        # delete the session in Django
                        Session.objects.filter(session_key=session_key).delete()

                    logout(request)
                    return redirect('login')

        response = self.get_response(request)
        return response