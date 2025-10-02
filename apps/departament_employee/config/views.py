#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required(login_url='login')
def departament_employee_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_departament_employee.html')
    else:
        return render(request, 'home_departament_employee.html')

