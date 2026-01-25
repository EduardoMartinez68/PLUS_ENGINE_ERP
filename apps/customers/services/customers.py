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
from django.db.models import Q
import os 

def save_customer(user, form, user_admin=None, password_admin=None):
    """
    Creates a client associated with the user's company.
    `form` must be a dictionary containing the form fields.
    """
    try:
        customer = Customer()
        customer.company = user.company
        customer.branch = user.branch

        # Personal information
        customer.sku = form.get("sku", "")
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
        customer.priority= form.get("priority") or 0
        customer.gender = form.get("gender") or ''

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
                img.close()
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
    Updates an existing customer that belongs to the user's company.
    `form` must be a dictionary containing the fields to update.
    """
    try:
        # Get the client only if it belongs to the user's company
        customer = Customer.objects.get(id=customer_id, company=user.company)

        #----- Personal information -----
        customer.sku = form.get("sku") or ''
        customer.name = form.get("name") or ''
        customer.email = form.get("email") or ''
        customer.phone = form.get("phone") or ''
        customer.cellphone = form.get("cellphone") or ''
        customer.country = form.get("country") or 'MX'
        customer.address = form.get("address") or ''
        customer.city = form.get("city") or ''
        customer.state = form.get("state") or ''
        customer.postal_code = form.get("postal_code") or ''
        customer.num_ext = form.get("num_ext") or ''
        customer.num_int = form.get("num_int") or ''
        customer.reference = form.get("reference") or ''
        customer.gender = form.get("gender") or ''

        customer.activated = Plus.to_bool(form.get("activated"))
        customer.priority = form.get("priority") or 0

        #----- Company info -----
        customer.this_customer_is_a_company = Plus.to_bool(form.get("this_customer_is_a_company"))

        customer.company_name = form.get("company_name") or ''
        customer.contact_name = form.get("contact_name") or ''
        customer.contact_email = form.get("contact_email") or ''
        customer.contact_phone = form.get("contact_phone") or ''
        customer.contact_cellphone = form.get("contact_cellphone") or ''
        customer.website = form.get("website") or ''
        customer.note = form.get("note") or ''

        #----- Customer company relations -----
        customer.points = form.get("points", customer.points or 0)
        customer.credit = form.get("credit", customer.credit or 0)
        customer.tags = form.get("tags") or []

        customer.number_of_price_of_sale = form.get("number_of_price_of_sale", customer.number_of_price_of_sale or 1)

        # Relación con CustomerType
        type_id = form.get("customer_type")
        if type_id:
            try:
                customer.customer_type = CustomerType.objects.get(id=type_id)
            except CustomerType.DoesNotExist:
                customer.customer_type = None

        # Relación con CustomerSource
        source_id = form.get("source")
        if source_id:
            try:
                customer.source = CustomerSource.objects.get(id=source_id)
            except CustomerSource.DoesNotExist:
                customer.source = None


        avatar_data = form.get("avatar")

        if avatar_data in ["None", None, ""]:  
            # if the server send a None → delete the avatar
            if customer.avatar:
                old_path = customer.avatar.path
                customer.avatar.delete(save=False)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except PermissionError:
                        pass
                customer.avatar = None
        elif avatar_data and "," in avatar_data:
            try:
                fmt, imgstr = avatar_data.split(",", 1)
                img_data = base64.b64decode(imgstr)

                # Procesar imagen
                with Image.open(BytesIO(img_data)) as img:
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")
                    img.thumbnail((400, 400), Image.LANCZOS)

                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=85, method=6)
                    buffer.seek(0)

                # Generar nombre único y reemplazar
                unique_filename = f"{uuid.uuid4().hex}_avatar.webp"

                # Si había una imagen previa, eliminarla
                if customer.avatar:
                    old_path = customer.avatar.path
                    customer.avatar.delete(save=False)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except PermissionError:
                            pass

                # Guardar la nueva
                customer.avatar.save(unique_filename, ContentFile(buffer.read()), save=False)

            except Exception as e:
                print("Error updating avatar:", e)

                
        # save the change
        customer.save()



        return {"success": True, "answer": "Customer updated successfully", "customer_id": customer.id}

    except Customer.DoesNotExist:
        return {"success": False, "error": "Customer not found or does not belong to your company"}
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

def search_customer_for_filter(user, search, customer_type, source, priority, activated):

    try:
        # --- 1. limit first to the user's company ---
        qs = Customer.objects.filter(company=user.company)

        
        # Filter by customer type
        if customer_type:
            qs = qs.filter(customer_type_id=customer_type)

        # Filter by source
        if source:
            qs = qs.filter(source_id=source)

        # Filter by priority
        if priority not in [None, ""]:
            qs = qs.filter(priority=priority)

        # Filter by activated
        if activated not in [None, ""]:
            if activated.lower() in ["true", "1", "yes", "on"]:
                qs = qs.filter(activated=True)
            elif activated.lower() in ["false", "0", "no", "off"]:
                qs = qs.filter(activated=False)

        qs = qs.order_by('-creation_date')

        # --- 2. apply memory search (decrypting fields) ---
        if search:
            search = search.lower()
            qs = [c for c in qs if (
                (c.sku and search in c.sku.lower()) or
                (c.name and search in c.name.lower()) or
                (c.email and search in c.email.lower()) or
                (c.phone and search in c.phone.lower()) or
                (c.cellphone and search in c.cellphone.lower())
            )]
  
        # --- 3. limit 20 answer ---
        qs = qs[:20]

        # --- 4. format the response ---
        customers = []
        for c in qs:
            customers.append({
                "id": c.id,
                "sku": c.sku or '',
                "name": c.name or '',
                "email": c.email or '',
                "phone": c.phone or '',
                "cellphone": c.cellphone or '',
                "country": c.country or '',
                "address": c.address or '',
                "city": c.city or '',
                "state": c.state or '',
                "postal_code": c.postal_code or '',
                "num_ext": c.num_ext or '',
                "num_int": c.num_int or '',
                "reference": c.reference or '',
                "this_customer_is_a_company": c.this_customer_is_a_company,

                "tag": ", ".join(c.tags) if c.tags else "",
                "points": float(c.points) if c.points else 0,
                "credit": float(c.credit) if c.credit else 0,
                "priority": c.priority,
                "customer_type": {
                    "id": c.customer_type.id if c.customer_type else None,
                    "name": c.customer_type.name if c.customer_type else None,
                    "color": c.customer_type.color if c.customer_type else None,
                    "description": c.customer_type.description if c.customer_type else None,
                } if c.customer_type else None,
                "source": {
                    "id": c.source.id if c.source else None,
                    "name": c.source.name if c.source else None,
                    "description": c.source.description if c.source else None,
                } if c.source else None,


                "avatar": c.avatar.url if c.avatar else None,
                "activated": "active" if c.activated else "inactive",
            })

        return {"success": True, "answer": customers, "error": "the serach of the customer was success"}
    
    except Exception as e:
        return {"success": False, "answer": [], "error": str(e)}
    
def get_information_of_a_customer_for_id(user, customer_id):
    try:
        if not customer_id:
            return {"success": False, "message": 'customer.message.error.this-id-customer-not-exist', "error": "Not exist this id of the customer in the database", "answer":""}
        
        #get the customer that exist in the dtabase
        customer = Customer.objects.get(id=customer_id, company=user.company)

        if not customer:
            return {"success": False, "message": "customer.message.error.this-id-customer-not-exist", "error": "Customer not found", "answer":""}
        
        #create the answer that send to the frontend or to other script that need this iformation
        data = {
            "id": customer.id,
            "sku": customer.sku or '',
            "name": customer.name or '',
            "email": customer.email or '',
            "phone": customer.phone or '',
            "cellphone": customer.cellphone or '',
            "gender": customer.gender or '',
            "country": customer.country or '',
            "address": customer.address or '',
            "city": customer.city or '',
            "state": customer.state or '',
            "postal_code": customer.postal_code or '',
            "num_ext": customer.num_ext or '',
            "num_int": customer.num_int or '',
            "reference": customer.reference or '',
            "this_customer_is_a_company": customer.this_customer_is_a_company,
            "company_name": customer.company_name or '',
            "contact_name": customer.contact_name or '',
            "contact_email": customer.contact_email or '',
            "contact_phone": customer.contact_phone or '',
            "contact_cellphone": customer.contact_cellphone or '',
            "website": customer.website or '',
            "points": float(customer.points) if customer.points else 0,
            "credit": float(customer.credit) if customer.credit else 0,
            "tags": customer.tags if customer.tags else [],
            "note": customer.note,
            "priority": customer.priority,
            "customer_type": {
                "id": customer.customer_type.id if customer.customer_type else None,
                "name": customer.customer_type.name if customer.customer_type else None,
                "color": customer.customer_type.color if customer.customer_type else None,
                "description": customer.customer_type.description if customer.customer_type else None,
            } if customer.customer_type else None,
            "source": {
                "id": customer.source.id if customer.source else None,
                "name": customer.source.name if customer.source else None,
                "description": customer.source.description if customer.source else None,
            } if customer.source else None,
            "avatar": customer.avatar.url if customer.avatar else '',
            "creation_date": customer.creation_date.isoformat() if customer.creation_date else None,
            "activated": customer.activated,
            "number_of_price_of_sale":customer.number_of_price_of_sale or 1
        }


        return {"success": True, "answer": data, "error": "The customer was found with success", 'message':'The customer was found'}

    except Exception as e:
        return {"success": False, "message": 'customer.message.error.exist-a-error-in-the-server', "error": f"Error: {str(e)}", "answer":""}
    
  
def change_status_of_the_customer(user, customer_id, status=False):
    try:
        if not customer_id:
            return {
                "success": False,
                "message": "customer.message.error.this-id-customer-not-exist",
                "answer":"",
                "error": "Missing customer_id",
            }

        # Busca el cliente dentro de la empresa del usuario
        customer = Customer.objects.filter(id=customer_id, company=user.company).first()

        if not customer:
            return {
                "success": False,
                "message": "customer.message.error.this-id-customer-not-exist",
                "answer":"",
                "error": "Customer not found or does not belong to this company",
            }

        # Desactivar al cliente
        customer.activated = status
        customer.save()

        return {
            "success": True,
            "message": "customer.message.success.customer-desactivated",
            "error": "",
            "answer": {
                "id": customer.id,
                "name": customer.name,
                "activated": customer.activated,
            },
        }

    except Exception as e:
        return {
            "success": False,
            "message": "customer.message.error.exist-a-error-in-the-server",
            "answer":"",
            "error": f"Error: {str(e)}",
        }
