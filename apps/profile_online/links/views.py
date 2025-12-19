from django.shortcuts import render

def profile_online_home(request):
    return render(request, 'home_profile_online.html')
