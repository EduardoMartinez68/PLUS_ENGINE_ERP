from django.shortcuts import render

def services_home(request):
    return render(request, 'home_services.html')
