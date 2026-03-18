from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription
admin.site.site_header = "PLUS Admin"
admin.site.site_title = "PLUS Admin"
admin.site.index_title = "Administration Panel PLUS"

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'max_messages', 'storage_gb')
    search_fields = ('name',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    #here is the display default that you will see when you enter in the admin of UserSubscription
    list_display = (
        'user_email', 
        'plan', 
        'status', 
        'current_period_end', 
        'created_at'
    )
    
    # Side filters to quickly find who has expired or who is on trial
    list_filter = ('status', 'plan', 'created_at')
    
    # Search by user's email (accessing the CustomUser model)
    search_fields = ('user__email', 'provider_subscription_id')
    
    # So you can manually edit the dates and plan
    readonly_fields = ('created_at', 'updated_at')

    # Helper to display the email in the list
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'



#-------------------------------------------------------------
from .models import Branch, Company, CustomUser
from django.conf import settings
import shutil
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class BranchInline(admin.TabularInline):
    model = Branch
    extra = 0
    fields = (
        'name_branch',
        'nickname',
        'country',
        'activated'
    )
    readonly_fields = ()
    show_change_link = True


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'company_name',
        'country',
        'support_email',
        'activated',
        'creation_date'
    )

    list_filter = (
        'activated',
        'country',
        'creation_date'
    )

    search_fields = (
        'company_name',
        'email_of_the_person_in_charge',
        'support_email'
    )

    ordering = ('-creation_date',)

    inlines = [BranchInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'logo',
                'company_name',
                'activated'
            )
        }),
        ('Main Contact', {
            'fields': (
                'name_of_the_person_in_charge',
                'email_of_the_person_in_charge',
                'phone',
                'cellphone'
            )
        }),
        ('Support & Web', {
            'fields': (
                'support_email',
                'website',
                'whatsapp_number'
            )
        }),
        ('Address', {
            'fields': (
                'address',
                'city',
                'state',
                'postal_code',
                'country'
            )
        }),
        ('Configuration', {
            'fields': (
                'default_currency',
                'timezone',
                'date_format'
            ),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': (
                'creation_date',
                'last_login'
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('creation_date',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name_branch',
        'company',
        'country',
        'activated',
        'creation_date'
    )

    list_filter = (
        'activated',
        'country',
        'company'
    )

    search_fields = (
        'name_branch',
        'company__company_name',
        'email_branch'
    )

    ordering = ('-creation_date',)

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'company',
                'name_branch',
                'nickname',
                'activated'
            )
        }),
        ('Contact', {
            'fields': (
                'email_branch',
                'support_email',
                'notification_email',
                'cellphone',
                'phone'
            )
        }),
        ('Address', {
            'fields': (
                'address',
                'postal_code',
                'country'
            )
        }),
        ('Settings', {
            'fields': (
                'default_currency',
                'default_language',
                'timezone'
            ),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': (
                'creation_date',
                'last_audit_date'
            ),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('creation_date',)


@receiver(pre_delete, sender=Branch)
def delete_branch_media_and_users(sender, instance, **kwargs):
    """
    Delete a branch:
    - delete all the user in the branch
    - delete the folder media/users/company_X/branch_Y
    """

    company_id = instance.company_id
    branch_id = instance.id

    # 1️⃣ here we will to delete all the user of the branch
    CustomUser.objects.filter(branch=instance).delete()

    # 2️⃣ delete folder of media
    if company_id and branch_id:
        branch_path = (
            settings.MEDIA_ROOT /
            f"users/company_{company_id}/branch_{branch_id}"
        )

        try:
            if branch_path.exists():
                shutil.rmtree(branch_path)
        except Exception as e:
            print(f"Error deleting branch media: {e}")

@receiver(pre_delete, sender=Company)
def delete_company_media_and_data(sender, instance, **kwargs):
    """
    Delete the company:
    - delete all the user in the company
    - delete all the branches
    - delete the folder media/users/company_X
    """

    company_id = instance.id

    # 1️⃣ delete all the user of the company
    CustomUser.objects.filter(company=instance).delete()

    # 2️⃣ delete the branch
    Branch.objects.filter(company=instance).delete()

    # 3️⃣ delete files media
    company_path = settings.MEDIA_ROOT / f"users/company_{company_id}"

    try:
        if company_path.exists():
            shutil.rmtree(company_path)
    except Exception as e:
        print(f"Error deleting company media: {e}")

