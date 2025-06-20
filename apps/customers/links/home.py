from django.shortcuts import render, redirect
from database.models import Customer
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def customers_home(request):
    id_branch = request.user.id_branch

    # Traer los primeros 20 resultados de ese branch ordenados por ID
    customers = Customer.objects.filter(id_branch=id_branch).order_by('id')[:20]

    return render(request, 'customers.html', {'customers': customers})




@csrf_exempt
def add_customer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # El body lo mandas en JSON con fetch

            name = data.get('name', '').strip()
            email = data.get('email')
            is_company = data.get('this_customer_is_a_company') in [True, 'true', 'on', '1']
            company_name = data.get('company_name')
            rfc = data.get('rfc')
            curp = data.get('curp')
            phone = data.get('phone')
            cellphone = data.get('cellphone')
            website = data.get('website')
            country = data.get('country')
            status = data.get('status') in [True, 'true', 'on', '1']

            if not name:
                return JsonResponse({'success': False, 'error': 'El nombre del cliente es obligatorio.'}, status=400)

            id_branch = request.user.id_branch
            creation_date = datetime.now()

            customer = Customer(
                id_branch=id_branch,
                name=name,
                email=email,
                this_customer_is_a_company=is_company,
                company_name=company_name,
                rfc=rfc,
                curp=curp,
                phone=phone,
                cellphone=cellphone,
                website=website,
                country=country,
                status=status,
                creation_date=creation_date
            )
            customer.save()

            return JsonResponse({'success': True, 'message': 'Cliente agregado exitosamente.'})

        except Exception as e:
            print('--------------------- ERROR al guardar cliente ---------------------')
            print(e)
            return JsonResponse({'success': False, 'error': f'Error al guardar cliente: {str(e)}'}, status=500)



    return render(request, 'addCustomer.html')
