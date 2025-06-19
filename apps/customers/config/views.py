from django.shortcuts import render

def customers_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'customers.html')
    else:
        return render(request, 'customers.html')

