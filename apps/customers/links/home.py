from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from django.http import HttpResponse
from ..models import Customer, CustomerType


def customers_home(request):
    # get the first 20 answers from the branch ordered by ID and that his status is True
    #customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
    customers=[]
    return render(request, 'customers.html', {'customers': customers})

#-------------------------customer-------------------------
from ..services.customers import save_customer, search_customer_for_filter, get_information_of_a_customer_for_id, change_status_of_the_customer, update_customer
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
            return JsonResponse({'success': False, 'error': f'Error in the server for save the customer: {str(e)}'}, status=500)



    return render(request, 'formCustomer.html')

def edit_customer(request, customer_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  #get the new information of the customer
            answer=update_customer(request.user,customer_id, data)

            #here we will see if can update the information
            if answer["success"]:
                return JsonResponse({'success': True, 'message': answer["answer"]}, status=200)
            else: 
                return JsonResponse({'success': False, 'error': f'Error to update the customer: {str(answer["error"])}'}, status=300)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error in the server for save the customer: {str(e)}'}, status=300)



    customer=get_information_of_a_customer_for_id(request.user, customer_id)
    return render(request, "formCustomer.html", {"customer": customer['answer']})



def customers_search(request):
    if request.method == "GET":
        all_filters = request.GET.get("allFilters", "")
        values = all_filters.split(",")

        search = values[0] if len(values) > 0 else ""
        customer_type = request.GET.get("customer_type")
        source = request.GET.get("source")
        priority = values[1] if len(values) > 1 else None
        activated = values[2] if len(values) > 2 else None

        answer = search_customer_for_filter(
            request.user, search, customer_type, source, priority, activated
        )

        if answer["success"]:
            return JsonResponse(
                {"success": True, "answer": answer["answer"], "error": answer["error"]},
                status=200
            )
        else:
            return JsonResponse(
                {"success": False, "answer": [], "error": str(answer["error"])},
                status=400
            )
    else:
        return JsonResponse(
            {"success": False, "error": "Method not permitted"},
            status=405
        )


@csrf_exempt
def get_information_of_the_customer(request):
    if request.method == "GET":
        customer_id = request.GET.get("id_customer")
        answer=get_information_of_a_customer_for_id(request.user, customer_id)
        return JsonResponse(
            {"success": answer['success'], "message": answer['message'], "answer": answer['answer'], 'error':answer['error']}, status=200
        ) 
        
    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=400
    ) 

def change_status_customer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        customer_id = data.get("customer_id")
        status = data.get("status", False)
        answer=change_status_of_the_customer(request.user,customer_id, status) 

        #we will see if can edit the status of the customer, else send a message of error to the frontend
        if answer['success']:
            #we will see if the customer be recover of the trash
            if status:
                return JsonResponse(
                    {"success": answer['success'], "message": 'customers.message.the-customer-was-recover', "answer": answer['answer'], 'error':answer['error']}, status=200
                ) 
            else:
                #we will see if need desactivate the customer 
                return JsonResponse(
                    {"success": answer['success'], "message": 'customer.message.success.customer-desactivated', "answer": answer['answer'], 'error':answer['error']}, status=200
                ) 
        else:
            return JsonResponse(
                {"success": answer['success'], "message": answer['message'], "answer": answer['answer'], 'error':answer['error']}, status=500
            )          
    
    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=400
    ) 

#--------------------------excel---------------------------------
def upload_customer_with_excel(request):
    return render(request, 'upload_customer.html') 

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