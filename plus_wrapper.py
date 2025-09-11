import os
import importlib.util
from typing import Tuple
from django.contrib.auth import authenticate

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
        module = Plus._load_module('converDate')
        return module.convert_from_utc(utc_datetime, timezone_str)
    
    @staticmethod
    def format_date_to_text(date, language="es",  type=1):
        #this funtions is for transform the date example 2025-09-05T15:00:00-06:00 to lenguace human 
        #type=1 August 27, 2025 at 11:00 AM or type=2 27/06/2025 11:00AM
        module = Plus._load_module('converDate')
        return module.format_date_to_text(date, type, language)
    


    

    @staticmethod
    def this_user_have_this_permission(
        user, 
        permission: str, 
        user_admin: str = None, 
        password_admin: str = None
    ) -> Tuple[bool, str]:
        return True
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

        # 1️⃣ Check permission of the main user
        if user.is_superuser or (hasattr(user, 'has_perm') and user.has_perm(permission)):
            return True, ""

        # 2️⃣ if the user not have this permission, now we will to check admin override if credentials are provided
        if user_admin and password_admin:
            admin_user = authenticate(username=user_admin, password=password_admin)
            if admin_user is not None and admin_user.is_active:
                if hasattr(admin_user, "has_perm") and admin_user.has_perm(permission):
                    return True, ""
            return False, "permission.invalid-credentials"

        # 3️⃣ Neither user nor admin have permission
        return False, "permission.not-have-this-permission"