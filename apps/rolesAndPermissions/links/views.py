from django.shortcuts import render

def rolesAndPermissions_home(request):
    return render(request, 'home_rolesAndPermissions.html')
