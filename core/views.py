from django.shortcuts import render
from core.readApps import APPS_CACHE #get the list of our apps in the ERP

def home(request):
    apps = APPS_CACHE
    return render(request, 'core/home.html',{'apps': apps})