from django.shortcuts import render
from database.models import Customer
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def customers_home(request):
    id_branch = 1  # por ejemplo, el branch que quieres filtrar

    # Traer los primeros 20 resultados de ese branch ordenados por ID
    customers = Customer.objects.filter(id_branch=id_branch).order_by('id')[:20]

    return render(request, 'customers.html', {'customers': customers})