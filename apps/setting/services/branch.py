from core.models import CustomUser, Company, Branch
from django.core.exceptions import ValidationError, ObjectDoesNotExist
def update_branch(user, data) -> dict:
    """
    Actualiza los datos de la sucursal asociada al usuario.
    data debe ser un diccionario con las claves del modelo Branch.
    Devuelve un dict con el resultado.
    """
    result = {"success": False, "message": "", "branch": None}

    branch = getattr(user, "branch", None)
    if not branch:
        result["message"] = "El usuario no tiene una sucursal asociada."
        return result

    try:
        updated_fields = []
        for field, value in data.items():
            if hasattr(branch, field):
                setattr(branch, field, value)
                updated_fields.append(field)

        #branch.updated_by = user.email or user.username
        #branch.save(update_fields=updated_fields + ["updated_by"])
        branch.save()

        result.update({
            "success": True,
            "message": "Sucursal actualizada correctamente.",
            "branch": branch
        })

    except ValidationError as e:
        result["message"] = f"Error de validación: {e.messages}"
    except Exception as e:
        result["message"] = f"Error al actualizar la sucursal: {str(e)}"

    return result