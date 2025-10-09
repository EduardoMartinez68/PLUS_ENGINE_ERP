from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch, UserRole, Role, UserDepartment
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

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)  # We haven't saved anything to add yet. company/branch
                user.email = form.cleaned_data['email']
                # 1️⃣ create a company
                company = Company.objects.create(company_name=f'Company of {user.email}')

                # 2️⃣ create a branch
                branch = Branch.objects.create(company=company, name_branch=f'Branch of {user.email}')
                
                # 3️⃣ create a default role
                role, created = UserRole.objects.get_or_create(
                    id_company=company,
                    name="Admin",
                    defaults={'description': 'Rol Admin'}
                )

                #basic permissions that a new user will have
                basic_permits = [
                    "view_department_employees", "add_department_employees", "update_department_employees", 
                    "view_profile", "update_profile"]  # example

                for code in basic_permits:
                    permit = Permit.objects.get(code=code)
                    Role.objects.get_or_create(role=role, permit=permit, defaults={'active': True})


                # 3️⃣ save the ids in user
                user.company = company
                user.branch = branch
                user.user_role = role

                user.set_password(form.cleaned_data['password1'])  # hash the password
                user.save()

                messages.success(request, f"{ml.get_message('success')}")
                return redirect('/login')  # or wherever you want to redirect after registration
            except Exception as e:
                messages.error(request, f"{ml.get_message('email_taken')} {str(e)}")
        else:
            messages.error(request, f"{ml.get_message('required_fields')}")
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