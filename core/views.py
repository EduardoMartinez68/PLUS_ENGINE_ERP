from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch, UserRole, Role, UserDepartment, Permit, CustomUser
import os
from django.contrib import messages
import re

#when tis we will read our file .env
from dotenv import load_dotenv 
from django.contrib.auth.decorators import login_required

load_dotenv()
KEY_TINYMCE = os.getenv('KEY_TINYMCE')

@login_required(login_url='login')
def home(request):
    apps = APPS_CACHE
    user = request.user
    company = user.company  # Company instance
    branch = user.branch  # Branch instance

    return render(request, 'core/home.html',{'apps': apps,'KEY_TINYMCE':KEY_TINYMCE,'user': user,'company': company,'branch': branch})

from django.shortcuts import render, redirect
from core.forms import SignUpForm



#here we will import the message for translate the ERP with the language of the user
import core.message_language as ml
from apps.rolesAndPermissions.services.permits import get_all_the_permissions
import json


def get_languages_of_the_erp():
    #if the user not have a login, now we will get all the language that exist in the system of home
    base_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'language')
    base_path = os.path.abspath(base_path)
    languages = [
        name for name in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, name))
    ]

    return languages

def register(request):
    import re

    is_valid = True
    error_message = None
    form_login = {}
    languages=get_languages_of_the_erp()

    if request.method == 'POST':
        def is_valid_email(email):
            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            return re.match(pattern, email) is not None

        data = request.POST  # QueryDict
        # --- Convertimos a diccionario plano ---
        form_login = {k: v[0] for k, v in data.lists()}


        # --- Check required fields ---
        required_fields = ['email', 'name', 'cellphone', 'country', 'password1', 'password2']
        missing_fields = [field for field in required_fields if not form_login[field]]
        if missing_fields:
            error_message = "home.message.please-fill-in-all-required-fields"
            is_valid = False

        # --- Validate passwords ---
        password1 = form_login['password1'].strip()
        password2 = form_login['password2'].strip()
        if password1 != password2 or not password1:
            error_message = 'home.error.the-password-not-be-equals'
            is_valid = False
        elif len(password1) < 8:
            error_message = 'home.error.the-password-is-very-short'
            is_valid = False
        elif not (re.search(r'[A-Z]', password1) and 
                  re.search(r'[a-z]', password1) and 
                  re.search(r'[0-9]', password1) and 
                  re.search(r'[!@#$%^&*(),.?":{}|<>]', password1)):
            error_message = 'home.error.the-password-need-more-characteres'
            is_valid = False

        # --- Validate cellphone ---
        cellphone_pattern = re.compile(r'^\+?\d{8,15}$')
        if not cellphone_pattern.match(form_login['cellphone']):
            error_message = "home.error.the-cellphone-no-exist"
            is_valid = False

        # --- Validate email ---
        emailUser=form_login['email'].strip().lower()
        if not is_valid_email(emailUser):
            error_message = "home.error.the-email-no-is-valid"
            is_valid = False

        # --- Check if email already exists ---
        if CustomUser.objects.filter(email=emailUser).exists():
            error_message = "home.error.email-already-exists"
            is_valid = False

        if is_valid:
            try:
                # --- Create user ---
                user = CustomUser.objects.create_user(
                    email=emailUser,
                    password=password1,
                    username=form_login['name'],
                    name=form_login['name'],
                    cellphone=form_login['cellphone'],
                    country=form_login['country'],
                    language = form_login['language'] if 'language' in form_login else 'es',
                    timezone = form_login['timezone'] if 'timezone' in form_login else 'America/Mexico_City'
                )

                # --- Create company ---
                company_name = form_login['name_company'] if 'name_company' in form_login else f'Company of {emailUser}'
                company = Company.objects.create(
                    company_name=company_name,
                    name_of_the_person_in_charge=form_login['name'],
                    email_of_the_person_in_charge=form_login['email'],
                    cellphone=form_login['cellphone'],
                    country=form_login['country'],
                    timezone = form_login['timezone'] if 'timezone' in form_login else 'America/Mexico_City'
                )

                # --- Create branch ---
                branch = Branch.objects.create(
                    company=company,
                    name_branch=company_name,
                    country=form_login['country'],
                    cellphone=form_login['cellphone'],
                    timezone = form_login['timezone'] if 'timezone' in form_login else 'America/Mexico_City'
                )

                # --- Create default role ---
                role, created = UserRole.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={'description': 'Rol Admin'}
                )

                # --- Assign all permissions that exist in the ERP---
                all_permissions = get_all_the_permissions()
                for app_name, perms_data in all_permissions.items():
                    if isinstance(perms_data, dict) and "permissions" in perms_data:
                        for code in perms_data["permissions"]:
                            permit, created = Permit.objects.get_or_create(code=code, defaults={'app': app_name})
                            Role.objects.get_or_create(role=role, permit=permit, defaults={'active': True})

                #---------departament of the user---------------
                department, created = UserDepartment.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={
                        "description": "",
                        "color": "#007bff",
                        "manager": user,
                        "activated": True,
                    },
                )


                # --- Assign user to company/branch/role ---
                user.company = company
                user.branch = branch
                user.user_role = role
                user.save()

                # --- Authenticate and log in automatically ---
                authenticated_user = authenticate(request, email=form_login['email'], password=password1)
                if authenticated_user:
                    login(request, authenticated_user)
                    return redirect('/home')

                messages_success = "home.message.the-user-was-register-with-success"
                return render(request, 'login.html', {'form_login': form_login, 'success_message': messages_success, 'languages': languages})

            except Exception as e:
                print(e)
                error_message = f"Error: {str(e)}"

    return render(request, 'login.html', {'form_login': form_login, 'error_message': error_message, 'languages': languages})





from django.contrib.auth import authenticate, login
from core.forms import LoginForm

def login_view(request):
    form = LoginForm()
    error_message = None

    if request.method == 'POST':
        email = request.POST['email'].strip().lower()
        password = request.POST['password']

        
        # Authenticate usando USERNAME_FIELD='email'
        user = CustomUser.objects.get(email=email)
        if user.check_password(password):
            login(request, user)
            return redirect('home')
        else:
            error_message = 'home.error.no-can-login'


    #if the user not have a login, now we will get all the language that exist in the system of home
    languages=get_languages_of_the_erp()


    return render(request, 'login.html', {'form': form, 'error_message': error_message, 'languages': languages})



#---------------------------------------------------------------HERE WE WILL TO CREATE THE WEB PUBLIC---------------------
from django.shortcuts import get_object_or_404
def view_profile(request, slug):
    from apps.profile_online.models import PublicProfile

    profile = (
        PublicProfile.objects
        .select_related("user")
        .prefetch_related(
            "services",
            "schedules",
            "locations",
            "reviews",
        )
        .filter(
            public_slug=slug,
            is_public=True
        )
        .first()
    )

    # if the profile not exist now we will to render a web of error
    if not profile:
        return render(
            request,
            "webs/profile_not_available.html",
            status=404  # SEO-friendly
        )

    # address
    main_location = next(
        (loc for loc in profile.locations.all() if loc.is_main),
        None
    )


    #here we will to see that picture use 
    DEFAULT_AVATAR = "https://cdn-icons-png.flaticon.com/512/2716/2716038.png"
    avatar_url = DEFAULT_AVATAR
    if profile.profile_image:
        avatar_url = profile.profile_image.url
    elif hasattr(profile.user, "avatar") and profile.user.avatar:
        avatar_url = profile.user.avatar.url


    context = {
        "profile": profile,
        "avatar_url": avatar_url,
        "main_location": main_location,
        "services": profile.services.filter(is_active=True).order_by("order"),
        "schedules": profile.schedules.all(),
        "reviews": profile.reviews.filter(is_approved=True),
    }

    return render(request, "webs/profile.html", context)
