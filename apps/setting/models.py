from django.db import models
from django.db import models
from core.models import Branch, Company, CustomUser

#here you can create the body of the database 
class NotificationSetting(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        null=True,
        blank=True
    )

    # example:
    # inventory
    # sales
    # appointments
    # payments
    type_notification = models.CharField(
        max_length=100,
        db_index=True
    )

    # configuration
    notify_by_email = models.BooleanField(default=True)
    notify_by_system = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            'company',
            'branch',
            'type_notification'
        )

    def __str__(self):
        return f"{self.company} - {self.type_notification}"
    

class NotificationSettingUser(models.Model):

    notification = models.ForeignKey(
        NotificationSetting,
        on_delete=models.CASCADE,
        related_name='users'
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notification_settings'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            'notification',
            'user'
        )

    def __str__(self):
        return f"{self.user} -> {self.notification.type_notification}"