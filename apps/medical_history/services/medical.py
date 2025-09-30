from ..models import MedicalInformation
from django.core.exceptions import ObjectDoesNotExist
from typing import Dict, Any, List
from apps.customers.models import Customer
from django.db import transaction
import uuid

'''
this function is for get the information that we will show in the screen of the frontend of the home. 
Need the user that is be the application from the frontend, the skull and the page that need.
'''
def get_information_medical_in_list(user, skull: str='', page:int=1, limit:int=20)->Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "medical-history.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    try:
        queryset = MedicalInformation.objects.filter(company=company).select_related("customer")

        # filter for skull if exist
        if skull:
            queryset = queryset.filter(skull__icontains=skull)

        queryset = queryset.order_by("-created_at")

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        results = queryset[start:end]


        #get the information that show in the screen of the frontend
        data = []
        for item in results:
            customer = item.customer
            data.append({
                "id": item.id,
                "skull": item.skull,
                "blood_type": item.blood_type,
                "created_at": item.created_at,
                "updated_at": item.updated_at,

                # ---- information of the customer ----
                "customer_id": customer.id,
                "avatar": customer.avatar.url if customer.avatar else None,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "cellphone": customer.cellphone,
            })



        return {
            "success": True,
            "answer": data,
            "error": 'Information get with success',
            #this information is for update the frontend 
            "pagination": {
                "page": page,
                "limit": limit,
                "total": queryset.count()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "answer": "medical-history.message.server.error.error-in-the-server",
            "error": str(e)
        }
    

def get_information_of_the_medical_history_for_customer_id(user, customer_id:int)->Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "medical-history.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    try:
        # First we get the customer that belongs to the same company
        customer = Customer.objects.get(id=customer_id, company=company)
    except ObjectDoesNotExist:
        return {
            "success": False,
            "answer": "medical-history.message.server.error.customer-not-found",
            "error": "Customer not found or not in your company"
        }

    # We obtain the customer's medical history (if any)
    try:
        medical_info = MedicalInformation.objects.get(customer=customer, company=company)
    except ObjectDoesNotExist:
        #if this customer not have a medical history we will to create
        with transaction.atomic():
            skull_identifier = str(uuid.uuid4())  # puedes cambiar esto a un uuid4() si prefieres
            medical_info = MedicalInformation.objects.create(
                company=company,
                customer=customer,
                skull=skull_identifier
            )

    # Construimos el diccionario que vamos a devolver
    data = {
        "id": customer.id,
        "avatar": customer.avatar.url if customer.avatar else None,
        "name": customer.name,
        "email": customer.email,
        "phone": customer.phone,
        "cellphone": customer.cellphone,
        "date_of_birth": customer.date_of_birth,
        "gender": customer.gender,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "postal_code": customer.postal_code,
        "num_ext": customer.num_ext,
        "num_int": customer.num_int,
        "reference": customer.reference,
        "company_name": customer.company_name,
        "this_customer_is_a_company": customer.this_customer_is_a_company,
        "points": customer.points,
        "credit": customer.credit,
        "tags": customer.tags,
        "customer_type": {
            "id": customer.customer_type.id if customer.customer_type else None,
            "name": customer.customer_type.name if customer.customer_type else None,
        } if customer.customer_type else None,
        "source": customer.source.name if customer.source else None,
        "priority": customer.priority,
        "activated": customer.activated,

        # Información médica
        "medical_info": {
            "skull": medical_info.skull if medical_info else None,
            "blood_type": medical_info.blood_type if medical_info else None,
            "height_cm": str(medical_info.height_cm) if medical_info and medical_info.height_cm else None,
            "weight_kg": str(medical_info.weight_kg) if medical_info and medical_info.weight_kg else None,
            "bmi": str(medical_info.bmi) if medical_info and medical_info.bmi else None,
            "chronic_conditions": medical_info.chronic_conditions if medical_info else None,
            "allergies": medical_info.allergies if medical_info else None,
            "medications": medical_info.medications if medical_info else None,
            "surgeries": medical_info.surgeries if medical_info else None,
            "immunizations": medical_info.immunizations if medical_info else None,
            "family_history": medical_info.family_history if medical_info else None,
            "lifestyle": medical_info.lifestyle if medical_info else None,
            "emergency_contact_name": medical_info.emergency_contact_name if medical_info else None,
            "emergency_contact_phone": medical_info.emergency_contact_phone if medical_info else None,
            "emergency_contact_relation": medical_info.emergency_contact_relation if medical_info else None,
            "last_visit": medical_info.last_visit if medical_info else None,
            "notes": medical_info.notes if medical_info else None,
            "info_other_doctor": medical_info.info_other_doctor if medical_info else None,
        } if medical_info else None
    }

    return {
        "success": True,
        "answer": data,
        "error": "Data get with success"
    }