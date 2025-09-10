#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..models import Customer
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
@login_required(login_url='login')
def customers_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        id_company = request.user.id_company
    
        # get the first 20 answers from the branch ordered by ID and that his status is True
        #customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
        customers=[]
        return render(request, 'customers.html', {'customers': customers})
    else:
        id_company = request.user.id_company
    
        # get the first 20 answers from the branch ordered by ID and that his status is True
        #customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
        customers=[]
        return render(request, 'customers.html', {'customers': customers})

@login_required(login_url='login')
def add_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

@login_required(login_url='login')
def edit_customer(request, id_customer):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

@login_required(login_url='login')
def customers_search(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET':
            #name, email, phone in the input of search
            #Tags (input)
            #type customer (select)
            #source (select)
            #Prioridad (select)
            #activated (select only true or not)
    
            customers = [
                {
                    "id": 1,
                    "name": "Luis Miguel",
                    "email": "luis.miguel@example.com",
                    "phone": "+52 444 123 4567",
                    "tag": "VIP",
                    "points": 1200,
                    "credit": 500.0,
                    "priority": "Alta",
                    "avatar": "https://example.com/avatars/luis.jpg",
                    "status": "active"
                },
                {
                    "id": 2,
                    "name": "Ana Torres",
                    "email": "ana.torres@example.com",
                    "phone": "+52 444 765 4321",
                    "tag": "Frecuente",
                    "points": 300,
                    "credit": 150.0,
                    "priority": "Media",
                    "avatar": "https://example.com/avatars/ana.jpg",
                    "status": "inactive"
                }
            ]
    
            return JsonResponse(
                {
                    "success": True,
                    "message": "Consulta exitosa",
                    "answer": customers
                },
                status=200
            )
    else:
        if request.method == 'GET':
            #name, email, phone in the input of search
            #Tags (input)
            #type customer (select)
            #source (select)
            #Prioridad (select)
            #activated (select only true or not)
    
            customers = [
                {
                    "id": 1,
                    "name": "Luis Miguel",
                    "email": "luis.miguel@example.com",
                    "phone": "+52 444 123 4567",
                    "tag": "VIP",
                    "points": 1200,
                    "credit": 500.0,
                    "priority": "Alta",
                    "avatar": "https://example.com/avatars/luis.jpg",
                    "status": "active"
                },
                {
                    "id": 2,
                    "name": "Ana Torres",
                    "email": "ana.torres@example.com",
                    "phone": "+52 444 765 4321",
                    "tag": "Frecuente",
                    "points": 300,
                    "credit": 150.0,
                    "priority": "Media",
                    "avatar": "https://example.com/avatars/ana.jpg",
                    "status": "inactive"
                }
            ]
    
            return JsonResponse(
                {
                    "success": True,
                    "message": "Consulta exitosa",
                    "answer": customers
                },
                status=200
            )

@login_required(login_url='login')
def get_information_of_the_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "GET":
            id_customer = request.GET.get("id_customer")
    
            data = {
                "id": id_customer,
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "phone": "444-123-4567",
                "cellphone": "444-987-6543",
                "country": "MX",
                "address": "Av. Universidad #123",
                "city": "San Luis Potosí",
                "state": "SLP",
                "postal_code": "78000",
                "num_ext": "15",
                "num_int": "2B",
                "reference": "Frente a la farmacia Guadalajara",
                "this_customer_is_a_company": False,
                "company_name": None,
                "contact_name": None,
                "website": None,
                "points": "150.00",
                "credit": "2000.00",
                "tags": ["VIP", "Frecuente"],
                "priority": 2,
                "customer_type": {
                    "id": 1,
                    "name": "Paciente",
                    "color": "#3498db",
                    "description": "Clientes que reciben atención médica"
                },
                "source": {
                    "id": 1,
                    "name": "Facebook Ads",
                    "description": "Campaña publicitaria en Facebook"
                },
                "avatar": "/media/customers/default.png",
                "creation_date": "2025-09-09T12:30:00",
                "activated": True
            }
    
            return JsonResponse({"success": True, "message": "Customer found", "answer": data}, status=200)
    
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)
    else:
        if request.method == "GET":
            id_customer = request.GET.get("id_customer")
    
            data = {
                "id": id_customer,
                "name": "Juan Pérez",
                "email": "juan.perez@example.com",
                "phone": "444-123-4567",
                "cellphone": "444-987-6543",
                "country": "MX",
                "address": "Av. Universidad #123",
                "city": "San Luis Potosí",
                "state": "SLP",
                "postal_code": "78000",
                "num_ext": "15",
                "num_int": "2B",
                "reference": "Frente a la farmacia Guadalajara",
                "this_customer_is_a_company": False,
                "company_name": None,
                "contact_name": None,
                "website": None,
                "points": "150.00",
                "credit": "2000.00",
                "tags": ["VIP", "Frecuente"],
                "priority": 2,
                "customer_type": {
                    "id": 1,
                    "name": "Paciente",
                    "color": "#3498db",
                    "description": "Clientes que reciben atención médica"
                },
                "source": {
                    "id": 1,
                    "name": "Facebook Ads",
                    "description": "Campaña publicitaria en Facebook"
                },
                "avatar": "/media/customers/default.png",
                "creation_date": "2025-09-09T12:30:00",
                "activated": True
            }
    
            return JsonResponse({"success": True, "message": "Customer found", "answer": data}, status=200)
    
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

@login_required(login_url='login')
def search_customers_select(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            result_list = []
    
            result_list.append({
                'id': 1,
                'text': 'pablo'
            })
            return JsonResponse({'success': True,'results': result_list})
        else:
            return JsonResponse({'message': 'Método no permitido'}, status=405)
    else:
        if request.method == 'POST':
            result_list = []
    
            result_list.append({
                'id': 1,
                'text': 'pablo'
            })
            return JsonResponse({'success': True,'results': result_list})
        else:
            return JsonResponse({'message': 'Método no permitido'}, status=405)

