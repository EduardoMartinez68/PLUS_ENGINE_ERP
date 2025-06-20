from django.shortcuts import render

def contracts_home(request):
    return render(request, 'home_contracts.html')


