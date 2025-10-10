from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch, UserRole, Role, UserDepartment, Permit
import os
from django.contrib import messages

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

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']

                # 1 Create a company
                company = Company.objects.create(company_name=f'Company of {user.email}')

                # 2 create a branch
                branch = Branch.objects.create(company=company, name_branch=f'Branch of {user.email}')

                # 3 create a rol for default
                role, created = UserRole.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={'description': 'Rol Admin'}
                )

                # 4 get all the permits in the ERP and we will to create
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

                # 5 save the relation like the user
                user.company = company
                user.branch = branch
                user.user_role = role
                user.set_password(form.cleaned_data['password1'])  # hash del password
                user.save()

                # 6 Authenticate and log in automatically
                authenticated_user = authenticate(request, email=user.email, password=form.cleaned_data['password1'])
                if authenticated_user is not None:
                    login(request, authenticated_user)  # login session automatic
                    messages.success(request, "home.message.welcome-user")
                    return redirect('/home')

                messages.success(request, "home.message.the-user-was-register-with-success")
                return redirect('/login')

            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "home.message.please-fill-in-all-required-fields")
    else:
        form = SignUpForm()

    return render(request, 'singup.html', {'form': form})


from django.contrib.auth import authenticate, login
from core.forms import LoginForm

def login_view(request):
    form = LoginForm()

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Django llamará automáticamente a EmailHashBackend
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, f"{ml.get_message('wrong_email_or_password')}")

    return render(request, 'login.html', {'form': form})