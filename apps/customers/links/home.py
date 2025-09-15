from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.http import HttpResponse
from ..models import Customer, CustomerType


def customers_home(request):
    company = request.user.company

    # get the first 20 answers from the branch ordered by ID and that his status is True
    #customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
    customers=[]
    return render(request, 'customers.html', {'customers': customers})

#-------------------------customer-------------------------
from django.views.decorators.csrf import csrf_exempt
import base64
import datetime
import decimal
from ..services.customers import save_customer, search_customer_for_filter
@csrf_exempt
def add_customer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # El body lo mandas en JSON con fetch
            answer=save_customer(request.user,data)
            if answer["success"]:
                return JsonResponse({'success': True, 'message': answer["answer"]}, status=200)
            else: 
                return JsonResponse({'success': False, 'error': f'Error to save the customer: {str(answer["error"])}'}, status=300)
        except Exception as e:
            print('--------------------- ERROR to save the customer ---------------------')
            print(e)
            
            return JsonResponse({'success': False, 'error': f'Error in the server for save the customer: {str(e)}'}, status=500)



    return render(request, 'formCustomer.html')

@csrf_exempt
def customers_search(request):
    if request.method == "GET":
        # --- 1. Obtener filtros desde request.GET ---
        search = request.GET.get("query", "").strip()  # text free
        customer_type = request.GET.get("customer_type")  # id o None
        source = request.GET.get("source")  # id o None
        priority = request.GET.get("priority")  # 0–3 o None
        activated = request.GET.get("activated")  # "true"/"false" o None

        answer=search_customer_for_filter(request.user,search,customer_type,source,priority, activated)
        if answer["success"]:
            return JsonResponse({'success': True, 'answer': answer["answer"], 'error':answer["error"]}, status=200)
        else: 
            return JsonResponse({'success': False, 'error': f'Error to search the customer: {str(answer["error"])}'}, status=300)
    else:
        return JsonResponse({'success': False, 'error': f'Method not permitted'}, status=300)

from django.shortcuts import get_object_or_404

@csrf_exempt
def get_information_of_the_customer(request):
    if request.method == "GET":
        try:
            id_customer = request.GET.get("id_customer")
            
            if not id_customer:
                return JsonResponse(
                    {"success": False, "message": "id_customer is requerid"},
                    status=400,
                )

            # Obtiene el cliente o devuelve 404 si no existe
            customer = get_object_or_404(Customer, id=id_customer)

            # Construir respuesta con todos los campos
            data = {
                "id": customer.id,
                "name": customer.name or '',
                "email": customer.email or '',
                "phone": customer.phone or '',
                "cellphone": customer.cellphone,
                "country": customer.country or '',
                "address": customer.address or '',
                "city": customer.city or '',
                "state": customer.state or '',
                "postal_code": customer.postal_code or '',
                "num_ext": customer.num_ext or '',
                "num_int": customer.num_int or '',
                "reference": customer.reference or '',
                "this_customer_is_a_company": customer.this_customer_is_a_company,
                "company_name": customer.company_name or '',
                "contact_name": customer.contact_name or '',
                "website": customer.website or '',
                "points": float(customer.points) if customer.points else 0,
                "credit": float(customer.credit) if customer.credit else 0,
                "tags": customer.tags if customer.tags else [],
                "priority": customer.priority,
                "customer_type": {
                    "id": customer.customer_type.id if customer.customer_type else None,
                    "name": customer.customer_type.name if customer.customer_type else None,
                    "color": customer.customer_type.color if customer.customer_type else None,
                    "description": customer.customer_type.description if customer.customer_type else None,
                } if customer.customer_type else None,
                "source": {
                    "id": customer.source.id if customer.source else None,
                    "name": customer.source.name if customer.source else None,
                    "description": customer.source.description if customer.source else None,
                } if customer.source else None,
                "avatar": customer.avatar.url if customer.avatar else None,
                "creation_date": customer.creation_date.isoformat() if customer.creation_date else None,
                "activated": customer.activated,
            }

            return JsonResponse(
                {"success": True, "message": "Customer found", "answer": data},
                status=200,
            )

        except Exception as e:
            print(e)
            return JsonResponse(
                {"success": False, "error": f"Error: {str(e)}"}, status=500
            )

    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=400
    ) 

#-------------------------type customer-------------------------
from ..services.type_customer import delete_type_customer_service, edit_type_customer_service, add_type_customer_service, search_type_customer_for_id_service, search_type_customer_service

@csrf_exempt
def search_type_customer(request):
    # Ensure request method is GET
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    # Extract query param
    query = request.GET.get("query", "").strip()

    # Call business logic
    answer, status = search_type_customer_service(request.user, query)
    return JsonResponse(answer, status=status)

def search_type_customer_for_id(request):
    # Ensure the request method is GET
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    # Extract ID from query params
    customer_type_id = request.GET.get("id", "").strip()

    # Call business logic
    result, status = search_type_customer_for_id_service(request.user, customer_type_id)
    return JsonResponse(result, status=status)

def add_type_customer(request):
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

def edit_type_customer(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"success": False, "message": "Invalid JSON", "error": str(e)}, status=400)

    result, status = edit_type_customer_service(request.user, data)
    return JsonResponse(result, status=status)

def delete_type_customer(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    data = json.loads(request.body)
    customer_type_id = data.get("id")
    answer, status = delete_type_customer_service(request.user, customer_type_id)
    return JsonResponse(answer, status=status)

#-------------------------type user-------------------------
from ..services.customer_source import get_customer_source, add_a_new_source, update_source, delete_a_source_with_his_id, get_source_by_id, get_customer_source_select

def get_customers_with_seeker(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    query = request.GET.get("query", "").strip()
    result = get_customer_source(request.user, query)

    return JsonResponse({"success": True, "answer": result}, status=200)

def search_source(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    query = request.GET.get("query", "").strip()
    result = get_customer_source_select(request.user, query)

    return JsonResponse({"success": True, "answer": result}, status=200)

def search_source_by_id(request):
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

def add_source(request):
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

def edit_source(request):
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

def delete_source(request):
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