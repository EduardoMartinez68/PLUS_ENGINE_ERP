from django.shortcuts import render


def customers_home(request):
    return render(request, 'customers.html')