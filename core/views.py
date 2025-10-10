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


def register(request):
    import re

    is_valid = True
    error_message = None
    form_login = {}

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

                # --- Assign all permissions ---
                all_permissions = get_all_the_permissions()
                for app_name, perms_list in all_permissions.items():
                    for code in perms_list:
                        permit, created = Permit.objects.get_or_create(code=code, defaults={'app': app_name})
                        Role.objects.get_or_create(role=role, permit=permit, defaults={'active': True})

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
                return render(request, 'login.html', {'form_login': form_login, 'success_message': messages_success})

            except Exception as e:
                print(e)
                error_message = f"Error: {str(e)}"

    return render(request, 'login.html', {'form_login': form_login, 'error_message': error_message})





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

    return render(request, 'login.html', {'form': form, 'error_message': error_message})