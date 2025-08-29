from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch
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
    company = user.id_company  # Company instance
    branch = user.id_branch  # Branch instance

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

                # 1️⃣ create a company
                company = Company.objects.create(company_name=f'Company of {user.email}')

                # 2️⃣ create a branch
                branch = Branch.objects.create(id_company=company, branch_name=f'Branch of {user.email}')

                # 3️⃣ save the ids in user
                user.id_company = company
                user.id_branch = branch


                messages.success(request, f"{ml.get_message('success')}")
                user.set_password(form.cleaned_data['password1'])  # hash the password
                user.save()

                return redirect('/login')  # or wherever you want to redirect after registration
            except Exception as e:
                messages.error(request, f"{ml.get_message('email_taken')} {str(e)}")
        else:
            messages.error(request, f"{ml.get_message('required_fields')}")
    else:
        form = SignUpForm()

    return render(request, 'singup.html', {'form': form})
