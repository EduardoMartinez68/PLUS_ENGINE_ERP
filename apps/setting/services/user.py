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
    

from django.utils.text import slugify
from django.db import IntegrityError, transaction
from ..plus_wrapper import Plus
def update_slug_user(user, data) -> dict:
    """
    Actualiza public_slug y is_public del usuario.
    """
    try:
        raw_slug = data.get("public_slug",None)
        is_public = Plus.to_bool(data.get("is_public",False))

        if not raw_slug:
            return {
                "success": False,
                "message": "setting.error.slug_required",
            }

        slug = slugify(raw_slug)
        if not slug:
            return {
                "success": False,
                "message": "setting.error.invalid_slug",
            }

        # Validar slug duplicado solo si cambia
        if slug != user.public_slug:
            if CustomUser.objects.filter(public_slug=slug).exclude(pk=user.pk).exists():
                return {
                    "success": False,
                    "message": "setting.error.slug_already_exists",
                }

        fields_to_update = []

        if user.public_slug != slug:
            user.public_slug = slug
            fields_to_update.append("public_slug")

        if user.is_public != is_public:
            user.is_public = is_public
            fields_to_update.append("is_public")

        if not fields_to_update:
            return {
                "success": True,
                "message": "setting.slug.no_changes",
                "slug": user.public_slug,
                "is_public": user.is_public,
            }

        with transaction.atomic():
            user.save(update_fields=fields_to_update)

        return {
            "success": True,
            "message": "setting.slug.updated",
            "slug": user.public_slug,
            "is_public": user.is_public,
        }

    except IntegrityError:
        return {
            "success": False,
            "message": "setting.error.slug_conflict",
        }

    except Exception as e:
        return {
            "success": False,
            "message": "setting.error.slug_conflict",
            "error": str(e),
        }