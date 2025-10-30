from core.models import CustomUser, Company, Branch
from django.core.exceptions import ValidationError, ObjectDoesNotExist
def update_user(user, data) -> dict:
    """
    Actualiza los datos configurables del usuario autenticado.
    Solo se permiten los siguientes campos:
    - language
    - decimal_separator
    - thousands_separator
    - timezone
    - date_format

    Retorna un diccionario con el resultado de la operación.
    """

    allowed_fields = [
        "language",
        "decimal_separator",
        "thousands_separator",
        "timezone",
        "date_format",
    ]

    # Validar tipo de usuario
    if not isinstance(user, CustomUser):
        return {
            "success": False,
            "message": "setting.error.the-data-of-the-user-not-be-valid",
            "error": "El objeto recibido no es un usuario válido.",
        }

    if not isinstance(data, dict):
        return {
            "success": False,
            "message": "setting.error.invalid-data-format",
            "error": "Los datos enviados no tienen el formato esperado (dict).",
        }

    updated = False

    try:
        for field in allowed_fields:
            if field in data:
                new_value = data[field]
                current_value = getattr(user, field, None)

                # Validación básica
                if new_value is None or new_value == "":
                    continue

                # Solo actualiza si cambia el valor
                if new_value != current_value:
                    setattr(user, field, new_value)
                    updated = True

        if not updated:
            return {
                "success": True,
                "message": "setting.error.not-exist-change-in-the-system",
                "error": "Not exist change in the system.",
            }

        # Intentar guardar
        user.save()
        return {
            "success": True,
            "message": "setting.success.user-update",
            "error": "",
        }

    except ValidationError as e:
        return {
            "success": False,
            "message": "setting.error.validation",
            "error": str(e),
        }

    except Exception as e:
        return {
            "success": False,
            "message": "setting.error.unexpected",
            "error": str(e),
        }