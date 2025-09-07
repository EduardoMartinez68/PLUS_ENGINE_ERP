from django.shortcuts import render

def products_home(request):
    return render(request, 'home_products.html')
