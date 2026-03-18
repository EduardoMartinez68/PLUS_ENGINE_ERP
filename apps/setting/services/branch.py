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


from django.utils import timezone
from core.models import WhatsAppAccount
def update_token_branch(user, data):
    access_token = data.get("access_token")
    phone_number_id = data.get("phone_number_id")

    if not access_token or not phone_number_id:
        return {
            "success": False,
            "message": "setting.error.not-exist-data-in-the-form-whatsapp"
        }

    # create or update the 'WhatsAppAccount' 
    whatsapp_account, created = WhatsAppAccount.objects.update_or_create(
        branch=user.branch,
        defaults={
            "company": user.company,
            "access_token": access_token,
            "phone_number_id": phone_number_id,
            "template_today":data.get("template_today", ""),
            "template_day_before":data.get("template_day_before", ""),
            "template_four_before":data.get("template_four_before", ""),
            "template_qualification":data.get("template_qualification", ""),
            "template_birthday":data.get("template_birthday", ""),
            "waba_id": data.get("waba_id", ""),
            "display_phone_number": data.get("display_phone_number", ""),
            "status": "connected",
            "token_expires_at": None,
            "messages_sent_this_month": 0,
        }
    )

    return {
        "success": True,
        "message": "branch update with success.",
    }


def get_whatsapp_credentials(user):
    if not user.branch:
        return {
            "success": False,
            "message": "El usuario no tiene sucursal asignada."
        }

    try:
        whatsapp_account = WhatsAppAccount.objects.get(branch=user.branch)
    except WhatsAppAccount.DoesNotExist:
        return {
            "success": False,
            "message": "La sucursal no tiene WhatsApp conectado."
        }

    # Validar estado
    if whatsapp_account.status != "connected":
        return {
            "success": False,
            "message": "La cuenta de WhatsApp no está activa."
        }

    # Validar límite mensual
    if not whatsapp_account.can_send_more:
        return {
            "success": False,
            "message": "Se alcanzó el límite mensual de mensajes."
        }

    # Validar expiración del token
    if whatsapp_account.token_expires_at and whatsapp_account.token_expires_at < timezone.now():
        return {
            "success": False,
            "message": "El token de WhatsApp ha expirado."
        }

    return {
        "success": True,
        "access_token": whatsapp_account.access_token,
        "phone_number_id": whatsapp_account.phone_number_id,
        "template_today":whatsapp_account.template_today,
        "template_day_before":whatsapp_account.template_day_before,
        "template_four_before":whatsapp_account.template_four_before,
        "template_qualification":whatsapp_account.template_qualification,
        "template_birthday":whatsapp_account.template_birthday
    }