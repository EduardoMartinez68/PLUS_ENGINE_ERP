from django.core.exceptions import ObjectDoesNotExist
from typing import Dict, Any, List
from apps.customers.models import Customer
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator
import uuid
from ..models import Odontogram, HistoryOdontogram, Tooth
from django.db.models import Q
from ..plus_wrapper import Plus

def get_or_create_odontogram(customer, doctor) -> 'Odontogram':
    """
    Obtiene o crea un odontograma para un paciente.
    Si no existe, lo crea automáticamente.
    """
    company = customer.company
    branch = customer.branch  # se asume que el cliente pertenece a una sucursal

    odontogram, created = Odontogram.objects.get_or_create(
        company=company,
        customer=customer,
        defaults={
            "branch": branch,
            "doctor": doctor,
        }
    )

    return odontogram


def get_odontograms(user, sku: str = '', page: int = 1, limit: int = 20) -> Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "odontograma.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    doctor = user

    #if exist a sku in the weeker
    if sku:
        qs = Customer.objects.filter(
            company=company
        )
 
        sku = sku.lower()
        qs = [c for c in qs if (
            (c.sku and sku in c.sku.lower()) or
            (c.name and sku in c.name.lower()) or
            (c.email and sku in c.email.lower()) or
            (c.phone and sku in c.phone.lower()) or
            (c.cellphone and sku in c.cellphone.lower())
        )]
        qs = qs[:20]
        customers=qs
    else:
        # if not exist a sku we get the first 20 odontograms
        customers = Customer.objects.filter(
            company=company,
            odontogram__doctor=doctor
        ).distinct()[:limit]

    results = []
    for c in customers:
        # Obtain or create the patient's odontogram 
        odontogram = get_or_create_odontogram(c, doctor)

        results.append({
            "sku": c.sku,
            "name": c.name,
            "email": c.email,
            "cellphone": c.cellphone,
            "gender": c.gender,
            "date_of_birth": c.date_of_birth,
            "avatar": c.avatar.url if c.avatar else None,

            "odontogram_id": odontogram.id,
            "odontogram_doctor": getattr(odontogram.doctor, "name", ""),
            "odontogram_svg": '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="#f5f5f5"/><circle cx="50" cy="50" r="30" fill="#e0e0e0"/></svg>',
            "odontogram_created_at": odontogram.created_at,
        })

    # Manual pagination
    paginator = Paginator(results, limit)
    page_obj = paginator.get_page(page)

    return {
        "success": True,
        "message": "odontograma.message.success.found",
        "answer": results,

        "page": page_obj.number,
        "total_pages": paginator.num_pages,
        "total_results": paginator.count,
        "results": list(page_obj)
    }

def get_information_odontograms(user, sku: str='', page:int=1, limit:int=20)->Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "odontograma.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    if not sku:
        return {
            "success": False,
            "answer": "odontograma.message.client.error.no-sku-provided",
            "error": "Customer SKU is required"
        }
    

    #here we will to try get the customer
    try:
        customer = Customer.objects.select_related("company", "branch").get(
            sku=sku, company=company
        )
    except Customer.DoesNotExist:
        return {
            "success": False,
            "answer": "odontograma.message.client.error.no-customer-found",
            "error": f"No customer found with SKU '{sku}' for this company"
        }

    #when get the customer now we will to get his odontogram
    odontogram = (
        Odontogram.objects.filter(company=company, customer=customer)
        .select_related("doctor", "branch")
        .prefetch_related("odontograms")  # por si se usa related_name en HistoryOdontogram
        .first()
    )


    #if the customer not have a odontograma, we will to create 
    if not odontogram:
        return {
            "success": False,
            "answer": "odontograma.message.client.error.no-odontogram-found",
            "error": f"No odontogram found for customer {customer.name}"
        }
    

    #return the struct 
    return {
        "success": True,
        "answer": "odontograma.message.success.found",
        "data": {
            "customer": {
                "sku": customer.sku,
                "name": customer.name,
                "email": customer.email,
                "cellphone": customer.cellphone,
                "gender": customer.gender,
                "date_of_birth": customer.date_of_birth,
                "avatar": customer.avatar.url if customer.avatar else None,
                "company": customer.company.name if customer.company else None,

                "odontogram_id": odontogram.id,
                "odontogram_doctor": getattr(odontogram.doctor, "name", ''),
                "odontogram_id": odontogram.id,
                "odontogram_created_at": odontogram.created_at,
            },
        }
    }


def add_new_odontogram(user, data)-> Dict[str, Any]:
    """
    Make a new odontogram for a patient.

    Args:
        user (CustomUser): he is the doctor that be create the odontogram.
        data (dict): This dictionary have:
            - 'customer_id': ID of the customer
            - 'history_name': Name or key of the first history
            - 'is_kid': bool for know if the odontogram is for a kid o an adult

    Returns:
        dict: Information from the created odontogram, including generated IDs.
    """


    # ------------------ Valid the form ------------------
    required_fields = ['customer_id',  'history_name']
    for field in required_fields:
        if field not in data:
            return {
                "success": False,
                "message": "odontograma.error.need-all-the-data",
                "error": f"The input '{field}' is requerid."
            }

    customer_id = data['customer_id']
    history_name = data['history_name']
    is_kid = Plus.to_bool(data.get('is_kid', False))

    #get all the models that need the odontogram
    customer = Customer.objects.get(id=customer_id)
    doctor = user
    company = doctor.company
    branch = doctor.branch


    #first we will see if the odontogram already exist in the company
    existing = Odontogram.objects.filter(
        company=company,
        customer=customer
    )

    if existing.exists():
        return {
            "success": False,
            "message": "odontograma.error.already-exist",
            "error": f"This patient already a odontogram in this company"
        }

    try:
        # ------------------ CREACIÓN DENTRO DE TRANSACCIÓN ------------------
        with transaction.atomic():
            #here we will to create the odontogram root
            odontogram = Odontogram.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                doctor=doctor,
            )

            # create the first history of the odontogram
            history = HistoryOdontogram.objects.create(
                customer=customer,
                key=history_name,
                notes=f"Odontogram create by {user.name or user.username}"
            )

            # Determine which teeth to create
            # Adult: 11–48 | Kid: 51–85
            teeth_range = []
            if not is_kid:
                teeth_range = [n for n in range(11, 19)] + [n for n in range(21, 29)] + \
                            [n for n in range(31, 39)] + [n for n in range(41, 49)]
            else:
                teeth_range = [n for n in range(51, 56)] + [n for n in range(61, 66)] + \
                            [n for n in range(71, 76)] + [n for n in range(81, 86)]

            # Create the tooth
            tooth_objects = [
                Tooth(
                    historyodontogram=history,
                    FDI_number=num,
                    name_key=dict(Tooth.FDI_TEETH).get(num, ""),
                    status="healthy"
                )
                for num in teeth_range
            ]
            Tooth.objects.bulk_create(tooth_objects)



        # ------------------ RETURN ------------------
        return {
            "success": True,
            "odontogram_id": odontogram.id,
            "history_id": history.id,
            "total_teeth_created": len(teeth_range),
            "is_kid": is_kid
        }



    except IntegrityError as e:
        return {
            "success": False,
            "message": "odontograma.error.integrity-error",
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "message": "odontograma.error.unexpected",
            "error": str(e)
        }



def get_latest_history_for_odontogram(user, odontogram_id: int) -> Dict[str, Any]:
    """
    Obtiene el historial más reciente de un odontograma con todos sus dientes.

    Args:
        odontogram_id (int): ID del Odontogram.

    Returns:
        Dict[str, Any]: Diccionario con la información del historial más reciente y sus dientes.
                        Retorna {} si no existe.
    """
    result: Dict[str, Any] = {}

    try:
        odontogram = Odontogram.objects.get(id=odontogram_id, doctor=user)
    except Odontogram.DoesNotExist:
        return {
            "success": False,
            "message": "odontograma.error.not-exist",
            "answer": {},
            "error": "This odontogram does not exist or you don't have permission"
        }

    # Obtener el historial más reciente para este paciente
    latest_history = HistoryOdontogram.objects.filter(
        customer=odontogram.customer,
    ).order_by('-created_at').first()

    if not latest_history:
        return result

    customer = odontogram.customer

    # Obtener todos los dientes asociados al historial
    teeth_qs = latest_history.teeth.all().order_by('FDI_number')
    teeth_data = [
        {
            "id": t.id,
            "FDI_number": t.FDI_number,
            "name_key": t.name_key,
            "status": t.status,
            
            "svg_state": t.svg_state,
            "surfaces":t.surfaces,

            "caries_depth": t.caries_depth,
            "has_tartar":t.has_tartar,
            "status_gum":t.status_gum,
            "mobility":t.mobility,

            "diagnosis":t.diagnosis or '',
            "treatments":t.treatments or '',
            "notes":t.notes or '',
            "last_checkup":t.last_checkup
        }
        for t in teeth_qs
    ]

    # Construir el resultado
    result = {
        "success":True,
        "answer":{
            "history_id": latest_history.id,
            "customer_id": latest_history.customer.id,
            "key": latest_history.key,
            "notes": latest_history.notes,
            "created_at": latest_history.created_at,
            "updated_at": latest_history.updated_at,
            "blocked": latest_history.blocked,
            "teeth": teeth_data,
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "avatar": customer.avatar.url if customer.avatar else None,
            }
        }
    }

    return result