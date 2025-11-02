from django.core.exceptions import ObjectDoesNotExist
from typing import Dict, Any, List
from apps.customers.models import Customer
from django.db import transaction
from django.core.paginator import Paginator
import uuid
from ..models import Odontogram
from django.db.models import Q

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

    doctor = user  # el doctor autenticado

    # Si hay un SKU, el doctor está buscando a un paciente en específico
    if sku:
        customers = Customer.objects.filter(
            company=company
        ).filter(
            Q(sku__icontains=sku) | Q(name__icontains=sku)
        )[:limit]
    else:
        # Si no hay SKU, obtenemos los primeros 20 odontogramas del doctor
        customers = Customer.objects.filter(
            company=company,
            odontogram__doctor=doctor
        ).distinct()[:limit]

    results = []
    for c in customers:
        # Obtener o crear el odontograma del paciente
        odontogram = get_or_create_odontogram(c, doctor)

        results.append({
            "customer": {
                "sku": c.sku,
                "name": c.name,
                "email": c.email,
                "cellphone": c.cellphone,
                "gender": c.gender,
                "date_of_birth": c.date_of_birth,
                "avatar": c.avatar.url if c.avatar else None,
                "company": c.company.name if c.company else None,

                "odontogram_id": odontogram.id,
                "odontogram_doctor": getattr(odontogram.doctor, "name", ""),
                "odontogram_created_at": odontogram.created_at,
            }
        })

    # Paginación manual (ya que usamos un queryset recortado)
    paginator = Paginator(results, limit)
    page_obj = paginator.get_page(page)

    return {
        "success": True,
        "answer": "odontograma.message.success.found",
        "data": {
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_results": paginator.count,
            "results": list(page_obj),
        }
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