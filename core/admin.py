from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'max_messages', 'storage_gb')
    search_fields = ('name',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    # Campos que verás en la lista principal
    list_display = ('user_email', 'plan', 'status', 'current_period_end', 'created_at')
    
    # Filtros laterales para encontrar rápido quién ha expirado o quién es trial
    list_filter = ('status', 'plan', 'created_at')
    
    # Buscador por el email del usuario (accediendo al modelo CustomUser)
    search_fields = ('user__email', 'provider_subscription_id')
    
    # Para que puedas editar las fechas y el plan manualmente
    readonly_fields = ('created_at', 'updated_at')

    # Helper para mostrar el email en la lista
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'