#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from database.models import Customer
from django.shortcuts import render
def customers_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        id_branch = 1  # por ejemplo, el branch que quieres filtrar
    
        # Traer los primeros 20 resultados de ese branch ordenados por ID
        customers = Customer.objects.filter(id_branch=id_branch).order_by('id')[:20]
    
        return render(request, 'customers.html', {'customers': customers})
    else:
        id_branch = 1  # por ejemplo, el branch que quieres filtrar
    
        # Traer los primeros 20 resultados de ese branch ordenados por ID
        customers = Customer.objects.filter(id_branch=id_branch).order_by('id')[:20]
    
        return render(request, 'customers.html', {'customers': customers})

