from django.shortcuts import render

def payroll_home(request):
    return render(request, 'payroll/home.html')
