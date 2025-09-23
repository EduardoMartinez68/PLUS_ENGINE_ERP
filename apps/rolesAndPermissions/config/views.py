#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required(login_url='login')
def rolesAndPermissions_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_rolesAndPermissions.html')
    else:
        return render(request, 'home_rolesAndPermissions.html')

