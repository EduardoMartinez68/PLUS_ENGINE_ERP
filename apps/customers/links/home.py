from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.http import HttpResponse
from ..models import Customer, CustomerType


def customers_home(request):
    id_company = request.user.id_company

    # get the first 20 answers from the branch ordered by ID and that his status is True
    #customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
    customers=[]
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



    return render(request, 'formCustomer.html')




@csrf_exempt
def customers_search(request):
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

@csrf_exempt
def get_information_of_the_customer(request):
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


    

#-------------------------type user-------------------------
@csrf_exempt
def search_type_customer(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    """
    Search customer types by query or return first 20 if query is empty.
    Only search in the company of the logged-in user.
    """
    user = request.user

    query = request.GET.get("query", "").strip()

    # We filter by the user's company
    types = CustomerType.objects.filter(company_id=request.user.id_company.id)

    if query:
        # We search for matches in the name (case-insensitive)
        types = types.filter(name__icontains=query)

    # we limit to 20 results
    types = types[:20]

    # We prepared the response in JSON format.
    data = [
        {
            "id": t.id,
            "text": t.name,
            "description": t.description,
            "color": t.color
        }
        for t in types
    ]

    return JsonResponse({"success": True, "answer": data})

def search_type_customer_for_id(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    customer_type_id = request.GET.get("id", "").strip()

    if not customer_type_id.isdigit():
        return JsonResponse({"success": False, "message": "Invalid ID"}, status=400)

    # filter for id and for the company of the user
    try:
        customer_type = CustomerType.objects.filter(
            company_id=request.user.id_company.id,
            id=int(customer_type_id)
        ).first()  # return None if not exist
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
    
    #if the type customer not exist return a message of error to the frontend
    if not customer_type:
        return JsonResponse({"success": False, "message": "message.this-type-customer-not-exist"}, status=404)

    data = {
        "id": customer_type.id,
        "name": customer_type.name,
        "description": customer_type.description,
        "color": customer_type.color
    }

    return JsonResponse({"success": True, "answer": data})

def add_type_customer(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))

        #get the information that send the frontend
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        color = data.get("color", "#3498db").strip()

        #we will see if exist the title of the type customer
        if not title:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-type-event", 'error':"Need the name of the type customer"}, status=200)

        #here we will see if exist this type customer in the company
        if CustomerType.objects.filter(company=request.user.id_company, name=title).exists():
            return JsonResponse({"success": False, "message": "message.this-name-exist-in-your-company", 'error':"This type customer already exist in the database"}, status=200)

        # Create the new customer type
        customer_type = CustomerType.objects.create(
            company=request.user.id_company,
            name=title,
            description=description,
            color=color,
        )

        answer={
            "id": customer_type.id,
            "name": customer_type.name,
            "color": customer_type.color,
            "description": customer_type.description
        }

        return JsonResponse({
            "success": True,
            "message": "Customer added with success",
            "answer": answer
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": "Error in the server", "error": str(e)}, status=500)
    
def edit_type_customer(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        customer_type_id = data.get("id")
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        color = data.get("color", "#3498db").strip()

        if not customer_type_id:
            return JsonResponse({"success": False, "message": "message.need-the-id-of-the-type-customer"}, status=400)

        if not title:
            return JsonResponse({"success": False, "message": "message.need-the-name-of-the-type-event"}, status=400)

        # Obtener el customer type dentro de la compañía del usuario
        try:
            customer_type = CustomerType.objects.get(
                id=customer_type_id,
                company=request.user.id_company  # <-- objeto Company
            )
        except CustomerType.DoesNotExist:
            return JsonResponse({"success": False, "message": "message.not-exist-this-type-customer-in-your-company"}, status=404)

        # Validar duplicados (otro CustomerType con el mismo nombre en la compañía)
        if CustomerType.objects.filter(
            company=request.user.id_company,  # <-- objeto Company
            name=title
        ).exclude(id=customer_type_id).exists():
            return JsonResponse({"success": False, "message": "message.this-name-exist-in-your-company"}, status=400)

        # Actualizar los valores
        customer_type.name = title
        customer_type.description = description
        customer_type.color = color
        customer_type.save()

        answer = {
            "id": customer_type.id,
            "name": customer_type.name,
            "color": customer_type.color,
            "description": customer_type.description
        }

        return JsonResponse({
            "success": True,
            "message": "Tipo de cliente actualizado con éxito",
            "answer": answer
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": "Error in the server", "error": str(e)}, status=500)

@csrf_exempt
def search_customers_select(request):
    if request.method == 'POST':
        result_list = []

        result_list.append({
            'id': 1,
            'text': 'pablo'
        })
        return JsonResponse({'success': True,'results': result_list})
    else:
        return JsonResponse({'message': 'Método no permitido'}, status=405)
