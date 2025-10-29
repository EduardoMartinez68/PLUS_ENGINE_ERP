from core.models import CustomUser, Company, Branch
from django.core.exceptions import ValidationError, ObjectDoesNotExist
def update_company(user, data) -> dict:
    """
    Actualiza los datos de la compañía asociada al usuario.
    data debe ser un diccionario con las claves del modelo Company.
    Devuelve un dict con el resultado.
    """
    result = {"success": False, "message": "", "company": None}

    company = getattr(user, "company", None)
    if not company:
        result["message"] = "El usuario no tiene una compañía asociada."
        return result

    try:
        # 🔹 Iteramos sobre las claves del diccionario y actualizamos
        for field, value in data.items():
            if hasattr(company, field):
                setattr(company, field, value)

        # 🔹 Audit info
        company.updated_by = user.email or user.username

        # 🔹 Guardamos los cambios (usa la validación interna del modelo)
        company.save()

        result.update({
            "success": True,
            "message": "Compañía actualizada correctamente.",
            "company": company
        })

    except ValidationError as e:
        result["message"] = f"error in: {e.messages}"
    except Exception as e:
        result["message"] = f"error when try update the company: {str(e)}"

    return result