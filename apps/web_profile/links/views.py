from django.shortcuts import render

def web_profile_home(request):
    return render(request, 'home_web_profile.html')
