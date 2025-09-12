from ..models import CustomerType
from django.http import JsonResponse




def add_type_customer_service(user, data):
    """
    Business logic to add a new CustomerType for the user's company.
    Returns (dict, status_code).
    """

    # Extract and sanitize input data
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    color = data.get("color", "#3498db").strip()

    # Validate required fields
    if not title:
        return {
            "success": False,
            "message": "message.need-the-name-of-the-type-event",
            "error": "Need the name of the type customer"
        }, 400

    # Check if another CustomerType with the same name already exists in the company
    if CustomerType.objects.filter(company=user.company, name=title).exists():
        return {
            "success": False,
            "message": "message.this-name-exist-in-your-company",
            "error": "This type customer already exists in the database"
        }, 400

    try:
        # Create the new CustomerType
        customer_type = CustomerType.objects.create(
            company=user.company,
            name=title,
            description=description,
            color=color,
        )

        # Build response payload
        answer = {
            "id": customer_type.id,
            "name": customer_type.name,
            "color": customer_type.color,
            "description": customer_type.description
        }

        return {
            "success": True,
            "message": "Customer added successfully",
            "answer": answer
        }, 201

    except Exception as e:
        return {
            "success": False,
            "message": "Error in the server",
            "error": str(e)
        }, 500

def edit_type_customer_service(user, data):
    """
    Edita un tipo de cliente en la compañía del usuario.
    Retorna (dict, status_code).
    """
    customer_type_id = data.get("id")
    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    color = data.get("color", "#3498db").strip()

    if not customer_type_id:
        return {"success": False, "message": "message.need-the-id-of-the-type-customer"}, 400

    if not title:
        return {"success": False, "message": "message.need-the-name-of-the-type-event"}, 400

    # Obtener el tipo de cliente dentro de la compañía del usuario
    try:
        customer_type = CustomerType.objects.get(
            id=customer_type_id,
            company=user.company
        )
    except CustomerType.DoesNotExist:
        return {"success": False, "message": "message.not-exist-this-type-customer-in-your-company"}, 404

    # Validar duplicados
    if CustomerType.objects.filter(
        company=user.company,
        name=title
    ).exclude(id=customer_type_id).exists():
        return {"success": False, "message": "message.this-name-exist-in-your-company"}, 400

    # Actualizar valores
    customer_type.name = title
    customer_type.description = description
    customer_type.color = color
    customer_type.save()

    answer = {
        "id": customer_type.id,
        "name": customer_type.name,
        "color": customer_type.color,
        "description": customer_type.description,
    }

    return {
        "success": True,
        "message": "The type customer was updated successfully",
        "answer": answer
    }, 200

def delete_type_customer_service(user, customer_type_id):
    try:
        customer_type = CustomerType.objects.filter(
            company_id=user.company.id,
            id=int(customer_type_id)
        ).first()
    except Exception as e:
        return {"success": False, "message": "", "error":str(e)}, 500

    if not customer_type:
        return {"success": False, "message": "message.this-type-customer-not-exist", "error":""}, 404

    try:
        customer_type.delete()
        return {"success": True, "message": "", "error":""}, 200
    except Exception as e:
        return {"success": False, "message": "message.this-type-customer-not-exist", "error":str(e)}, 500

def search_type_customer_service(user, query, quantity=20):
    """
    Business logic to search customer types by query.
    If query is empty, returns the first 20 results.
    Only searches within the user's company.
    Returns (dict, status_code).
    """

    try:
        # Filter by company
        types = CustomerType.objects.filter(company_id=user.company.id)

        # Apply query filter if provided
        if query:
            types = types.filter(name__icontains=query)

        # Limit to 20 results
        types = types[:quantity]

        # Build response data
        data = [
            {
                "id": t.id,
                "name": t.name,
                "text": t.name,
                "description": t.description,
                "color": t.color
            }
            for t in types
        ]

        return {"success": True, "answer": data}, 200

    except Exception as e:
        return {"success": False, "message": "Error in the server", "error": str(e)}, 500
    
def search_type_customer_for_id_service(user, customer_type_id):
    """
    Business logic to search a CustomerType by ID within the user's company.
    Returns (dict, status_code).
    """

    # Validate ID format
    if not customer_type_id.isdigit():
        return {"success": False, "message": "Invalid ID"}, 400

    try:
        # Query the CustomerType by company and id
        customer_type = CustomerType.objects.filter(
            company_id=user.company.id,
            id=int(customer_type_id)
        ).first()
    except Exception as e:
        return {"success": False, "message": str(e)}, 500

    # If not found, return error
    if not customer_type:
        return {"success": False, "message": "message.this-type-customer-not-exist"}, 404

    # Build response payload
    data = {
        "id": customer_type.id,
        "name": customer_type.name,
        "description": customer_type.description,
        "color": customer_type.color
    }

    return {"success": True, "answer": data}, 200