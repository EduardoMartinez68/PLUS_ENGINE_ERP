from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP

def home(request):
    apps = APPS_CACHE
    return render(request, 'core/home.html',{'apps': apps})

from django.shortcuts import render, redirect
from core.forms import SignUpForm

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/login')  # o a donde quieras mandar después del registro
    else:
        form = SignUpForm()

    return render(request, 'singup.html', {'form': form})
