import base64
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import base64
import uuid
from cryptography.fernet import Fernet
from ..models import Customer, CustomerType, CustomerSource
from ..plus_wrapper import Plus
from django.core.exceptions import ValidationError


 
def save_customer(user, form, user_admin=None, password_admin=None):
    """
    Creates a client associated with the user's company.
    `form` must be a dictionary containing the form fields.
    """
    if not user.company:
        return {"success": False, "error": "User has no company assigned"}
    if not user.branch:
        return {"success": False, "error": "User has no branch assigned"}
    

    try:
        customer = Customer()
        customer.company = user.company
        customer.branch = user.branch

        # Personal information
        customer.name = form.get("name", "")
        customer.email = form.get("email") or None
        customer.phone = form.get("phone") or None
        customer.cellphone = form.get("cellphone") or None
        customer.country = form.get("country", "MX")
        customer.address = form.get("address") or None
        customer.city = form.get("city") or None
        customer.state = form.get("state") or None
        customer.postal_code = form.get("postal_code") or None
        customer.num_ext = form.get("num_ext") or None
        customer.num_int = form.get("num_int") or None
        customer.reference = form.get("reference") or None
        customer.activated = Plus.to_bool(form.get("activated"))

        # information of the company of the customer
        customer.this_customer_is_a_company = Plus.to_bool(form.get("this_customer_is_a_company"))
        customer.company_name = form.get("company_name") or None
        customer.contact_name = form.get("contact_name") or None
        customer.contact_email = form.get("contact_email") or None
        customer.contact_phone = form.get("contact_phone") or None
        customer.contact_cellphone = form.get("contact_cellphone") or None
        customer.website = form.get("website") or None
        customer.note = form.get("note") or None

        # information of the customer in the company
        customer.points = form.get("points") or 0
        customer.credit = form.get("credit") or 0
        customer.tags = form.get("tags") or None
        customer.number_of_price_of_sale = form.get("number_of_price_of_sale") or 1 #forever the price be 1 for default

        # do a relation with CustomerType and CustomerSource
        type_id = form.get("customer_type")
        if type_id:
            try:
                customer.customer_type = CustomerType.objects.get(id=type_id)
            except CustomerType.DoesNotExist:
                customer.customer_type = None

        source_id = form.get("source")
        if source_id:
            try:
                customer.source = CustomerSource.objects.get(id=source_id)
            except CustomerSource.DoesNotExist:
                customer.source = None

        #here we will see if exist a image in base64
        avatar_data = form.get("avatar")
        if avatar_data and "," in avatar_data:
            try:
                fmt, imgstr = avatar_data.split(",", 1)
                # decodificar imagen
                img_data = base64.b64decode(imgstr)
                img = Image.open(BytesIO(img_data))

                # Convertir a RGB si tiene alpha (webp soporta alpha, pero RGB suele ser más compatible)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Redimensionar a tamaño máximo recomendable para avatar
                max_size = (400, 400)
                img.thumbnail(max_size, Image.LANCZOS)

                # Guardar en memoria en formato WebP (liviano)
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=85, method=6)
                buffer.seek(0)

                # Nombre único para la imagen
                unique_filename = f"{uuid.uuid4().hex}_avatar.webp"
                customer.avatar.save(unique_filename, ContentFile(buffer.read()), save=False)
            except Exception as e:
                print("Error al procesar avatar:", e)


        customer.save()
        return {"success": True, "answer": "Customer save with success", "customer_id": customer.id}
    except Exception as e:
        print("Error saving customer:", e)
        import traceback
        traceback.print_exc() 
        return {"success": False, "error": str(
            e
        )}


def update_customer(user, customer_id, form):
    """
    Updates an existing customer and their avatar if provided.
    `form` must be a dictionary containing the fields to update.
    """
    try:
        # Obtener el cliente existente
        customer = Customer.objects.get(id=customer_id)

        #----- Personal information -----
        if "name" in form:
            customer.name = form.get("name")
        if "email" in form:
            customer.email = form.get("email") or None
        if "phone" in form:
            customer.phone = form.get("phone") or None
        if "cellphone" in form:
            customer.cellphone = form.get("cellphone") or None
        if "country" in form:
            customer.country = form.get("country", "MX")
        if "address" in form:
            customer.address = form.get("address") or None
        if "city" in form:
            customer.city = form.get("city") or None
        if "state" in form:
            customer.state = form.get("state") or None
        if "postal_code" in form:
            customer.postal_code = form.get("postal_code") or None
        if "num_ext" in form:
            customer.num_ext = form.get("num_ext") or None
        if "num_int" in form:
            customer.num_int = form.get("num_int") or None
        if "reference" in form:
            customer.reference = form.get("reference") or None
        if "activated" in form:
            customer.activated = Plus.to_bool(form.get("activated"))

        #----- Company info -----
        if "this_customer_is_a_company" in form:
            customer.this_customer_is_a_company = Plus.to_bool(form.get("this_customer_is_a_company"))
        if "company_name" in form:
            customer.company_name = form.get("company_name") or None
        if "contact_name" in form:
            customer.contact_name = form.get("contact_name") or None
        if "contact_email" in form:
            customer.contact_email = form.get("contact_email") or None
        if "contact_phone" in form:
            customer.contact_phone = form.get("contact_phone") or None
        if "contact_cellphone" in form:
            customer.contact_cellphone = form.get("contact_cellphone") or None
        if "website" in form:
            customer.website = form.get("website") or None
        if "note" in form:
            customer.note = form.get("note") or None

        #----- Customer company relations -----
        if "points" in form:
            customer.points = form.get("points") or 0
        if "credit" in form:
            customer.credit = form.get("credit") or 0
        if "tags" in form:
            customer.tags = form.get("tags") or None
        if "number_of_price_of_sale" in form:
            customer.number_of_price_of_sale = form.get("number_of_price_of_sale") or 1

        if "customer_type" in form:
            type_id = form.get("customer_type")
            if type_id:
                try:
                    customer.customer_type = CustomerType.objects.get(id=type_id)
                except CustomerType.DoesNotExist:
                    customer.customer_type = None

        if "source" in form:
            source_id = form.get("source")
            if source_id:
                try:
                    customer.source = CustomerSource.objects.get(id=source_id)
                except CustomerSource.DoesNotExist:
                    customer.source = None

        #----- Avatar -----
        avatar_data = form.get("avatar")
        if avatar_data and "," in avatar_data:
            try:
                fmt, imgstr = avatar_data.split(",", 1)
                img_data = base64.b64decode(imgstr)
                img = Image.open(BytesIO(img_data))

                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                max_size = (400, 400)
                img.thumbnail(max_size, Image.LANCZOS)

                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=85, method=6)
                buffer.seek(0)

                unique_filename = f"{uuid.uuid4().hex}_avatar.webp"
                customer.avatar.save(unique_filename, ContentFile(buffer.read()), save=False)
            except Exception as e:
                print("Error al procesar avatar:", e)

        # Guardar los cambios
        customer.save()
        return {"success": True, "answer": "Customer updated successfully", "customer_id": customer.id}

    except Customer.DoesNotExist:
        return {"success": False, "error": "Customer not found"}
    except Exception as e:
        print("Error updating customer:", e)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def toggle_customer_activation(customer_id, activate=True):
    """
    Activa o desactiva un cliente.
    
    Args:
        customer_id (int): ID del cliente a modificar.
        activate (bool): True para activar, False para desactivar.
    
    Returns:
        dict: Resultado de la operación.
    """
    try:
        customer = Customer.objects.get(id=customer_id)
        customer.activated = bool(activate)
        customer.save()
        status = "activated" if activate else "deactivated"
        return {"success": True, "message": f"Customer {status} successfully", "customer_id": customer.id}
    except Customer.DoesNotExist:
        return {"success": False, "error": "Customer not found"}
    except Exception as e:
        print("Error toggling customer activation:", e)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}