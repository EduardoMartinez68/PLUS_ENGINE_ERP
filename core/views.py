from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch, UserRole, Role, UserDepartment, Permit
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
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def register(request):
    is_valid=True
    error_message=None

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        try:
            data = json.loads(request.body)
        except Exception as e:
            error_message=e
            return render(request, 'login.html', {'form': form, 'error_message': error_message})   
        
        
        #here we will see if have all the information need for create a company in the database 
        required_fields = ['email', 'name', 'cellphone', 'country', 'password1', 'password2']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            error_message = f"home.message.please-fill-in-all-required-fields"
            is_valid = False

        #now we will see if the form be success 
        password1 = data.get('password1', '').strip()
        password2 = data.get('password2', '').strip()

        if password1!=password2 or password1=='':
            error_message='home.error.the-password-not-be-equals'
            is_valid=False 

        #we will see if the user add a cellphone valid
        cellphone_pattern = re.compile(r'^\+?\d{8,15}$')  #optionally allows + at the beginning
        if not cellphone_pattern.match(data.get('password1', '')):
            error_message = "home.error.the-cellphone-no-exist"
            is_valid = False

        if not is_valid_email(data.get('email', '')):
            error_message = "home.error.the-email-no-is-valid"
            is_valid = False

        #we will see if all the information of the form is valid and if is valid we will try of add the user to the database
        if is_valid:
            try:
                #1 create the information of the user
                user = form.save(commit=False)
                user.email = data['email']
                user.username = data['name']
                user.name = data['name']
                user.cellphone = data['cellphone']
                user.country = data['country'] or 'MX'
                user.language = data['language'] or 'es'
                user.timezone = data('timezone') or 'America/Mexico_City'
                user.set_password(data['password1'])  # hash del password

                # 2 Create a company
                company = Company.objects.create(
                    company_name=f'Company of {user.email}',
                    name_of_the_person_in_charge=user.name,
                    email_of_the_person_in_charge=user.email,
                    cellphone=user.cellphone,
                    country=user.country,
                    timezone=user.timezone
                )

                # 3 create a branch
                branch = Branch.objects.create(
                    company=company,
                    name_branch=f'Branch of {user.email}',
                    country=user.country,
                    cellphone=user.cellphone,
                    timezone=user.timezone
                )

                # 4 create a rol for default
                role, created = UserRole.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={'description': 'Rol Admin'}
                )

                # 5 get all the permits in the ERP and we will to create
                all_permissions = get_all_the_permissions()

                for app_name, app_data in all_permissions.items():
                    perms_list = app_data.get("permissions", [])
                    for code in perms_list:
                        try:
                            permit = Permit.objects.get(code=code)
                            Role.objects.get_or_create(role=role, permit=permit, defaults={'active': True})
                        except Permit.DoesNotExist:
                            # if the permit not exist in the database, we will to create the permit
                            permit = Permit.objects.create(code=code, app=app_name)
                            Role.objects.create(role=role, permit=permit, active=True)

                # 6 save the relation like the user
                user.company = company
                user.branch = branch
                user.user_role = role
                user.save()

                # 7 Authenticate and log in automatically
                authenticated_user = authenticate(request, email=user.email, password=form.cleaned_data['password1'])
                if authenticated_user is not None:
                    login(request, authenticated_user)  # login session automatic
                    return redirect('/home')

                messages_success="home.message.the-user-was-register-with-success"
                return render(request, 'login.html', {'form': form, 'error_message': messages_success})

            except Exception as e:
                error_message=f"Error: {str(e)}"

    else:
        form = SignUpForm()

    return render(request, 'login.html', {'form': form, 'error_message': error_message})


from django.contrib.auth import authenticate, login
from core.forms import LoginForm

def login_view(request):
    form = LoginForm()
    error_message = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Django will automatically call EmailHashBackend
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            error_message = 'home.error.no-can-login'

    return render(request, 'login.html', {'form': form, 'error_message': error_message})