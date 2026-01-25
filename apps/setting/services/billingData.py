from core.models import Branch, BranchBillingData
from django.core.exceptions import ValidationError, ObjectDoesNotExist

def update_branch_billing_data(branch, data) -> dict:
    """
    Crea o actualiza los datos de facturación (BranchBillingData)
    asociados a una sucursal (branch).

    Si la sucursal no tiene datos de facturación, los crea.
    Si ya existen, los actualiza con los campos recibidos en 'data'.

    Retorna un diccionario con:
        - success: bool
        - message: str
        - billing_data: instancia de BranchBillingData o None
        - error: descripción técnica del error (si aplica)
    """

    result = {"success": False, "message": "", "billing_data": None, "error": ""}

    # --- Validar branch ---
    if not isinstance(branch, Branch):
        result["message"] = "La sucursal no es válida."
        result["error"] = "El parámetro 'branch' no es una instancia de Branch."
        return result

    try:
        # Obtener o crear el registro de facturación asociado
        billing_data, created = BranchBillingData.objects.get_or_create(
            branch=branch,
            defaults={
                "company": branch.company,
                "country": getattr(branch.company, "country", "MX") or "MX"
            }
        )

        # Actualizar campos válidos dinámicamente
        updated_fields = []
        for field, value in data.items():
            if hasattr(billing_data, field):
                current_value = getattr(billing_data, field)
                if value != current_value:
                    setattr(billing_data, field, value)
                    updated_fields.append(field)

        if not updated_fields and not created:
            result.update({
                "success": False,
                "message": "No se detectaron cambios en los datos de facturación.",
                "billing_data": billing_data,
            })
            return result

        # Guardar los cambios
        billing_data.save()

        # Mensaje final
        result.update({
            "success": True,
            "message": "Datos de facturación actualizados correctamente." if not created else "Datos de facturación creados correctamente.",
            "billing_data": billing_data,
        })

    except ValidationError as e:
        result["message"] = "Error de validación en los datos de facturación."
        result["error"] = str(e)
    except Exception as e:
        result["message"] = "Error al guardar los datos de facturación."
        result["error"] = str(e)

    return result


def get_branch_billing_data(branch) -> dict:
    """
    Obtiene o crea los datos de facturación asociados a una sucursal (branch).
    Si no existen, los crea con valores por defecto.
    Devuelve un diccionario con la información lista para enviarse como JSON.
    """
    result = {"success": False, "message": "", "answer": None}

    if not branch:
        result["message"] = "No se proporcionó una sucursal válida."
        return result

    try:
        # Obtiene o crea los datos de facturación
        billing_data, created = BranchBillingData.objects.get_or_create(
            branch=branch,
            defaults={
                "company": branch.company,
                "legal_name": branch.company.name if hasattr(branch.company, "name") else "Sin nombre fiscal",
                "country": getattr(branch, "country", "MX") or "MX",
                "fiscal_engine": "generic",
            },
        )

        # Serializamos los campos relevantes
        result["answer"] = {
            "id": billing_data.id,
            "company_id": billing_data.company.id if billing_data.company else None,
            "branch_id": billing_data.branch.id,
            "tax_id": billing_data.tax_id or "",
            "secondary_id": billing_data.secondary_id or "",
            "legal_name": billing_data.legal_name or "",
            "street": billing_data.street or "",
            "num_ins": billing_data.num_ins or "",
            "num_out": billing_data.num_out or "",
            "city": billing_data.city or "",
            "state": billing_data.state or "",
            "municipality": billing_data.municipality or "",
            "cologne": billing_data.cologne or "",
            "postal_code": billing_data.postal_code or "",
            "country": billing_data.country or "",
            "fiscal_engine": billing_data.fiscal_engine or "",
            "is_active": billing_data.is_active,
            "notes": billing_data.notes or "",
            "created_at": billing_data.created_at.isoformat(),
            "updated_at": billing_data.updated_at.isoformat(),
        }

        result["success"] = True
        result["message"] = (
            "Datos de facturación creados correctamente."
            if created
            else "Datos de facturación obtenidos correctamente."
        )

    except Exception as e:
        result["error"] = f"Error al obtener o crear los datos de facturación: {str(e)}"

    return result