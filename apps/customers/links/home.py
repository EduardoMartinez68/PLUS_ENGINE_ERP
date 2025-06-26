from django.shortcuts import render, redirect
from database.models import Customer
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.http import HttpResponse

def customers_home(request):
    id_branch = request.user.id_branch

    # get the first 20 answers from the branch ordered by ID and that his status is True
    customers = Customer.objects.filter(id_branch=id_branch, status=True).order_by('id')[:20]

    return render(request, 'customers.html', {'customers': customers})



@csrf_exempt
def edit_customer(request, id_customer):
    if request.method == 'POST':
            try:
                data = json.loads(request.body)

                name = data.get('name', '').strip()
                email = data.get('email', '').strip()
                is_company = data.get('this_customer_is_a_company') in [True, 'true', 'on', '1']
                company_name = data.get('company_name', '').strip()
                rfc = data.get('rfc', '').strip()
                curp = data.get('curp', '').strip()
                phone = data.get('phone', '').strip()
                cellphone = data.get('cellphone', '').strip()
                website = data.get('website', '').strip()
                country = data.get('country', '').strip()
                status = data.get('this_customer_is_a_company') in [True, 'true', 'on', '1']

                if not name:
                    return JsonResponse({'success': False, 'message': 'El nombre del cliente es obligatorio.', 'error': ''}, status=400)

                try:
                    customer = Customer.objects.get(id=id_customer, id_branch=request.user.id_branch)
                except Customer.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Cliente no encontrado.', 'error': ''}, status=404)

                # Actualizar campos
                customer.name = name
                customer.email = email
                customer.this_customer_is_a_company = is_company
                customer.company_name = company_name
                customer.rfc = rfc
                customer.curp = curp
                customer.phone = phone
                customer.cellphone = cellphone
                customer.website = website
                customer.country = country
                customer.status = status
                customer.save()

                return JsonResponse({'success': True, 'message': 'Cliente editado exitosamente.'})

            except Exception as e:
                print('--------------------- ERROR edit_customer ---------------------')
                print(e)
                return JsonResponse({'success': False, 'message': 'Error al editar el cliente.', 'error': str(e)}, status=500)


    # GET
    try:
        customer = Customer.objects.get(id=id_customer)
    except Customer.DoesNotExist:
        return HttpResponse("Cliente no encontrado.", status=404)

    return render(request, 'formCustomer.html', {'customer': customer})




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



    return render(request, 'formCustomer.html')



@csrf_exempt
def search_customers(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        all_filters = data.get('allFilters', [])
        query = all_filters[0].strip() if len(all_filters) > 0 else ''
        status = all_filters[1].strip().lower() if len(all_filters) > 1 else ''

        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(email__icontains=query)
        )

        if status == 'true':
            customers = customers.filter(status=True)
        elif status == 'false':
            customers = customers.filter(status=False)

        result_list = []
        for c in customers:
            result_list.append({
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'cellphone': c.cellphone,
                'company_name': c.company_name
            })

        return JsonResponse({'success': True,'results': result_list})
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)