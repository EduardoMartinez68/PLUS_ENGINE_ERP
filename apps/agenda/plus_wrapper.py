import os
import importlib.util
from typing import Tuple
from django.contrib.auth import authenticate
from datetime import datetime

class Plus:
    functions_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../../functions')
    )

    @staticmethod
    def _load_module(module_name):
        module_file = os.path.join(Plus.functions_path, f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def convert_to_utc(date_str, timezone_str):
        # UTC stands for "Coordinated Universal Time."
        # It is the standard time reference throughout the world.
        # All time zones are defined relative to UTC.
        # For example:
        # - Mexico City is at UTC-6 in standard time
        # - Madrid is at UTC+1 in standard time
        #
        # When working with dates in programming:
        # 1. UTC allows you to store and compare dates regardless of the user's location.
        # 2. Converting to UTC prevents errors when users are in different time zones.
        # 3. In web applications, databases, and APIs, it is common to use UTC internally.
        #
        # Practical example:
        # 2025-08-28 12:00:00 UTC
        # is the exact same time worldwide, but will be displayed according to the local time zone:
        # - Mexico City: 06:00 AM (UTC-6)
        # - Madrid: 02:00 PM (UTC+2 in daylight saving time)
        module = Plus._load_module('converDate')
        return module.convert_to_utc(date_str, timezone_str)

    @staticmethod
    def convert_from_utc(utc_datetime, timezone_str):
        #this funtions converts a UTC datetime to a specific timezone
    
        # if is a string, try convert to datetime first
        if isinstance(utc_datetime, str):
            try:
                utc_datetime = datetime.fromisoformat(utc_datetime)
            except ValueError:
                #If it fails, we return the rope as is
                return utc_datetime
        module = Plus._load_module('converDate')
        converted = module.convert_from_utc(utc_datetime, timezone_str)
        return converted
    

    
    @staticmethod
    def format_date_to_text(date, language="es",  type=1):
        #this funtions is for transform the date example 2025-09-05T15:00:00-06:00 to lenguace human 
        #type=1 August 27, 2025 at 11:00 AM or type=2 27/06/2025 11:00AM
        module = Plus._load_module('converDate')

        dateText=date
        if isinstance(date, datetime):
            dateText=date.isoformat()
            
        
        return module.format_date_to_text(dateText, type, language)  # If it is already a rope, we return it as is
    

    def to_bool(value):
        return str(value).lower() in ("True","true", "on", "1")
    
    @staticmethod
    def valid_subscription(
        user, 
        service: str, 
    ) -> Tuple[bool, str]:
        """
        Check if the user has a the subscription need for do this activate.

        Parameters:
        - user: Django User object
        - service (str): Service codename to check
        Returns:
        - Tuple[bool, str]: 
            - True and empty string if permission is granted
            - False and an error message if the user not have the pack of the subscription that need
        """

        
        # 1️⃣ Check the subscription of the user and see if exist 
        from core.models import UserSubscription
        sub=UserSubscription.objects.filter(user=user).first()

        if not sub:
            return {
                "status": False,
                "message": "subscription.not-exist-this-suscription",
            }

        #if the subscription is expired
        if sub.is_expired():
            return {
                "status": False,
                "message": "subscription.your-subscription-is-expired",
            }
        
        #now we will see that would like do to the user 
        if service=='customers':
            return {
                "status": sub.can_create_client(),
                "message": "subscription.not-can-add-more-customers",
            }
        
        if service=='appointments':
            return {
                "status": sub.can_create_appointment(),
                "message": "subscription.not-can-add-more-appointsments",
            }
        

        if service=='employees':
            return {
                "status": sub.can_create_employee(),
                "message": "subscription.not-can-add-more-employees",
            }

        if service=='messages_whatsapp':
            return {
                "status": sub.can_send_message(),
                "message": "subscription.not-can-add-send-more-messages",
            }
        
        if service=='upload':
            return {
                "status": sub.can_upload_more_storage(),
                "message": "subscription.not-can-add-upload-more-files",
            }
        

        #for default we will return false and a message of that not exist this service
        return {
            "status": False,
            "message": "subscription.this-service-does-not-exist",
        }



    @staticmethod
    def this_user_have_this_permission(
        user, 
        permission: str, 
        user_admin: str = None, 
        password_admin: str = None
    ) -> Tuple[bool, str]:
        """
        Check if the user has a specific permission, or if admin credentials have it.

        Parameters:
        - user: Django User object
        - permission (str): Permission codename to check
        - user_admin (str): Optional username of an admin user to check if user lacks permission
        - password_admin (str): Password of the admin user

        Returns:
        - Tuple[bool, str]: 
            - True and empty string if permission is granted
            - False and an error message if permission is denied
        """

        from core.models import Role
        # 1️⃣ Check permission of the main user
        # related to the intermediate user-role table

        if Role.objects.filter(
            role=user.user_role,
            permit__code=permission,
            active=True
        ).exists():
            return True

        # 2️⃣ if the user not have this permission, now we will to check admin override if credentials are provided
        if user_admin and password_admin:
            admin_user = authenticate(username=user_admin, password=password_admin)
            if admin_user is not None and admin_user.is_active:
                #if exist this user admin, now we will check if this user have the permission
                if Role.objects.filter(role__userrole__user=admin_user,   permit__code=permission,active=True).exists():
                    return True #, ""
            return False #, "permission.invalid-credentials"

        # 3️⃣ Neither user nor admin have permission
        return False #, "permission.not-have-this-permission"
    

    def get_user_permissions(user, permissions_list):
        """
        get un user and do a list of all the permissions of the user.
        return a dictionary:
        {
            "permission1": True,
            "permission2": False,
            ...
        }
        """
        permissions = {}
        for perm_name in permissions_list:
            try:
                permissions[perm_name] = Plus.this_user_have_this_permission(user, perm_name)
            except Exception:
                permissions[perm_name] = False  # if exist a error return False
        return permissions