from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP
from core.models import Company, Branch
import os

#when tis we will read our file .env
from dotenv import load_dotenv 
load_dotenv()
KEY_TINYMCE = os.getenv('KEY_TINYMCE')


def home(request):
    apps = APPS_CACHE
    return render(request, 'core/home.html',{'apps': apps,'KEY_TINYMCE':KEY_TINYMCE})

from django.shortcuts import render, redirect
from core.forms import SignUpForm

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # todavía no guardamos para agregar company/branch

            # 1️⃣ Crear Company
            company = Company.objects.create(name=f'Empresa de {user.email}')

            # 2️⃣ Crear Branch
            branch = Branch.objects.create(id_company=company)

            # 3️⃣ Guardar en user los id
            user.id_company = company.id
            user.id_branch = branch.id

            user.set_password(form.cleaned_data['password1'])  # hash de password
            user.save()

            return redirect('/login')  # o a donde quieras mandar después del registro
    else:
        form = SignUpForm()

    return render(request, 'singup.html', {'form': form})
