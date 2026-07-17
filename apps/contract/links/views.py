from django.shortcuts import render

def contract_home(request):
    return render(request, 'contract/home.html')
