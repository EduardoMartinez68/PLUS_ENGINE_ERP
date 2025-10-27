from django.shortcuts import render

def setting_home(request):
    return render(request, 'home_setting.html')
