#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.customer_source import get_customer_source, add_a_new_source, update_source, delete_a_source_with_his_id, get_source_by_id, get_customer_source_select
from ..services.type_customer import delete_type_customer_service, edit_type_customer_service, add_type_customer_service, search_type_customer_for_id_service, search_type_customer_service
from ..services.customers import save_customer
from ..models import Customer, CustomerType
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
                print(data)
    
            except Exception as e:
                print('--------------------- ERROR al guardar cliente ---------------------')
                print(e)
                return JsonResponse({'success': False, 'error': f'Error al guardar cliente: {str(e)}'}, status=500)
    
    
    
        return render(request, 'formCustomer.html')
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)  # El body lo mandas en JSON con fetch
                print(data)
    
            except Exception as e:
                print('--------------------- ERROR al guardar cliente ---------------------')
                print(e)
                return JsonResponse({'success': False, 'error': f'Error al guardar cliente: {str(e)}'}, status=500)
    
    
    
        return render(request, 'formCustomer.html')

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
def search_type_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Ensure request method is GET
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        # Extract query param
        query = request.GET.get("query", "").strip()
    
        # Call business logic
        answer, status = search_type_customer_service(request.user, query)
        return JsonResponse(answer, status=status)
    else:
        # Ensure request method is GET
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        # Extract query param
        query = request.GET.get("query", "").strip()
    
        # Call business logic
        answer, status = search_type_customer_service(request.user, query)
        return JsonResponse(answer, status=status)

@login_required(login_url='login')
def search_type_customer_for_id(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Ensure the request method is GET
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        # Extract ID from query params
        customer_type_id = request.GET.get("id", "").strip()
    
        # Call business logic
        result, status = search_type_customer_for_id_service(request.user, customer_type_id)
        return JsonResponse(result, status=status)
    else:
        # Ensure the request method is GET
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        # Extract ID from query params
        customer_type_id = request.GET.get("id", "").strip()
    
        # Call business logic
        result, status = search_type_customer_for_id_service(request.user, customer_type_id)
        return JsonResponse(result, status=status)

@login_required(login_url='login')
def add_type_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Ensure the request method is POST
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        # Parse request body as JSON
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return JsonResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status=400)
    
        # Call business logic from service
        result, status = add_type_customer_service(request.user, data)
        return JsonResponse(result, status=status)
    else:
        # Ensure the request method is POST
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        # Parse request body as JSON
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return JsonResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status=400)
    
        # Call business logic from service
        result, status = add_type_customer_service(request.user, data)
        return JsonResponse(result, status=status)

@login_required(login_url='login')
def edit_type_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return JsonResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status=400)
    
        result, status = edit_type_customer_service(request.user, data)
        return JsonResponse(result, status=status)
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return JsonResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status=400)
    
        result, status = edit_type_customer_service(request.user, data)
        return JsonResponse(result, status=status)

@login_required(login_url='login')
def delete_type_customer(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        data = json.loads(request.body)
        customer_type_id = data.get("id")
        answer, status = delete_type_customer_service(request.user, customer_type_id)
        return JsonResponse(answer, status=status)
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        data = json.loads(request.body)
        customer_type_id = data.get("id")
        answer, status = delete_type_customer_service(request.user, customer_type_id)
        return JsonResponse(answer, status=status)

@login_required(login_url='login')
def get_customers_with_seeker(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        query = request.GET.get("query", "").strip()
        result = get_customer_source(request.user, query)
    
        return JsonResponse({"success": True, "answer": result}, status=200)
    else:
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        query = request.GET.get("query", "").strip()
        result = get_customer_source(request.user, query)
    
        return JsonResponse({"success": True, "answer": result}, status=200)

@login_required(login_url='login')
def search_source(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        query = request.GET.get("query", "").strip()
        result = get_customer_source_select(request.user, query)
    
        return JsonResponse({"success": True, "answer": result}, status=200)
    else:
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        query = request.GET.get("query", "").strip()
        result = get_customer_source_select(request.user, query)
    
        return JsonResponse({"success": True, "answer": result}, status=200)

@login_required(login_url='login')
def search_source_by_id(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({"success": False, "message":"Invalid request method","error": "Invalid request method"}, status=405)
    
        source_id = request.GET.get("id")
        if not source_id:
            return JsonResponse({"success": False, "message": "message.need-the-id-of-the-source", "error": "The source ID is required"}, status=400)
    
        try:
            source_id = int(source_id)
        except ValueError:
            return JsonResponse({"success": False, "message": "The source ID must be an integer", "error": "The source ID must be an integer"}, status=400)
    
        answer = get_source_by_id(request.user, source_id)
        return JsonResponse(answer, status=200 if answer["success"] else 404)
    else:
        if request.method != "GET":
            return JsonResponse({"success": False, "message":"Invalid request method","error": "Invalid request method"}, status=405)
    
        source_id = request.GET.get("id")
        if not source_id:
            return JsonResponse({"success": False, "message": "message.need-the-id-of-the-source", "error": "The source ID is required"}, status=400)
    
        try:
            source_id = int(source_id)
        except ValueError:
            return JsonResponse({"success": False, "message": "The source ID must be an integer", "error": "The source ID must be an integer"}, status=400)
    
        answer = get_source_by_id(request.user, source_id)
        return JsonResponse(answer, status=200 if answer["success"] else 404)

@login_required(login_url='login')
def add_source(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Not can do this", "error":"Invalid request method"}, status=405)
    
        # get all the field that the frontend send
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
        if not name:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-source", 'error':"the name is obligatory"}, status=400)
    
        answer = add_a_new_source(request.user, name, description)
        return JsonResponse(answer, status=200 if answer["success"] else 400)
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Not can do this", "error":"Invalid request method"}, status=405)
    
        # get all the field that the frontend send
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
        except Exception:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    
        if not name:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-source", 'error':"the name is obligatory"}, status=400)
    
        answer = add_a_new_source(request.user, name, description)
        return JsonResponse(answer, status=200 if answer["success"] else 400)

@login_required(login_url='login')
def edit_source(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            #get the data that send the frontend
            data = json.loads(request.body)
            source_id = data.get("id")
            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    
        if not source_id:
            return JsonResponse({"success": False, "message": "message.need-the-id-of-the-source", "error": "The source ID is required"}, status=400)
        if not name:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-source", "error":"The name not exist"}, status=400)
    
        answer = update_source(request.user, source_id, name, description)
        return JsonResponse(answer, status=200 if answer["success"] else 400)
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            #get the data that send the frontend
            data = json.loads(request.body)
            source_id = data.get("id")
            name = data.get("name", "").strip()
            description = data.get("description", "").strip()
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    
        if not source_id:
            return JsonResponse({"success": False, "message": "message.need-the-id-of-the-source", "error": "The source ID is required"}, status=400)
        if not name:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-source", "error":"The name not exist"}, status=400)
    
        answer = update_source(request.user, source_id, name, description)
        return JsonResponse(answer, status=200 if answer["success"] else 400)

@login_required(login_url='login')
def delete_source(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            data = json.loads(request.body)
            source_id = data.get("id")
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    
        if not source_id:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-source", "error": "The source ID is required"}, status=400)
    
        answer = delete_a_source_with_his_id(request.user, source_id)
        return JsonResponse(answer, status=200 if answer["success"] else 400)
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            data = json.loads(request.body)
            source_id = data.get("id")
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)
    
        if not source_id:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-source", "error": "The source ID is required"}, status=400)
    
        answer = delete_a_source_with_his_id(request.user, source_id)
        return JsonResponse(answer, status=200 if answer["success"] else 400)

