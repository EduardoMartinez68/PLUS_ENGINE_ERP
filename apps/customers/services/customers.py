import base64
from django.core.files.base import ContentFile
from PIL import Image
from io import BytesIO
import base64
import uuid

from apps.customers.services.forms import CustomerForm, CustomerUpdateForm
from ..models import Customer, CustomerType, CustomerSource
from ..plus_wrapper import Plus
from django.core.exceptions import ValidationError
from django.db.models import Q
import os 
from django.core.files.base import ContentFile
from cryptography.fernet import Fernet #this is for encrypt the file
from django.core.paginator import Paginator

#get the key of encrypt that is in our file .env
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY').encode()
f = Fernet(FIELD_ENCRYPTION_KEY)



def save_customer(user, form_data):
    form = CustomerForm(form_data)

    if not form.is_valid():
        return {
            "success": False,
            "errors": form.errors
        }

    customer = form.save(commit=False)
    customer.company = user.company
    customer.branch = user.branch
    customer.number_of_price_of_sale = customer.number_of_price_of_sale or 1

    avatar_data = form_data.get("avatar")
    if avatar_data:
        process_and_encrypt_avatar_form(customer, avatar_data)

    customer.save()

    return {
        "success": True,
        "customer_id": customer.id
    }

def process_and_encrypt_avatar_form(customer, avatar_data):
    """
    avatar_data: base64 string
    fernet: Fernet instance (key already loaded)
    """

    fmt, imgstr = avatar_data.split(",", 1)
    img_bytes = base64.b64decode(imgstr)

    img = Image.open(BytesIO(img_bytes))

    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img.thumbnail((400, 400), Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="WEBP", quality=85)
    img.close()

    raw_bytes = buffer.getvalue()

    # 🔐 ENCRIPTACIÓN REAL
    encrypted_bytes = f.encrypt(raw_bytes)

    filename = f"{uuid.uuid4().hex}.enc"
    customer.avatar.save(
        filename,
        ContentFile(encrypted_bytes),
        save=False
    )

def process_and_encrypt_avatar(avatar_base64):
    """
    Procesa una imagen base64, la convierte a WEBP, la encripta
    y retorna (filename, encrypted_bytes)
    """
    global f
    fmt, imgstr = avatar_base64.split(",", 1)
    img_data = base64.b64decode(imgstr)

    with Image.open(BytesIO(img_data)) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail((400, 400), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format="WEBP", quality=85, method=6)
        raw_bytes = buffer.getvalue()

    encrypted_bytes = f.encrypt(raw_bytes)
    filename = f"{uuid.uuid4().hex}.encrypted"

    return filename, encrypted_bytes

def update_customer(user, customer_id, data):
    try:
        customer = Customer.objects.get(
            id=customer_id,
            company=user.company
        )

        form = CustomerUpdateForm(data, instance=customer)

        if not form.is_valid():
            return {
                "success": False,
                "errors": form.errors
            }

        customer = form.save(commit=False)
        customer.save()

        # ---------- Avatar ----------
        avatar_data = data.get("avatar")

        if avatar_data in ["None", None, ""]:
            if customer.avatar:
                old_path = customer.avatar.path
                customer.avatar.delete(save=False)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except PermissionError:
                        pass

        elif avatar_data and "," in avatar_data:
            #delete the old avatar
            old_path = customer.avatar.path
            customer.avatar.delete(save=False)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except PermissionError:
                    pass
            process_and_encrypt_avatar_form(customer, avatar_data)

        customer.save()

        return {
            "success": True,
            "answer": "Customer updated successfully",
            "customer_id": customer.id
        }

    except Customer.DoesNotExist:
        return {
            "success": False,
            "error": "Customer not found or does not belong to your company"
        }
    
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

def search_customer_for_filter(user, search, customer_type, source, priority, activated, page=1):

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
        else:
            qs = list(qs)


        paginator = Paginator(qs, 20)
        try:
            page_obj = paginator.get_page(page)
        except:
            page_obj = paginator.get_page(1)

        page_items = page_obj.object_list

        # --- 4. format the response ---
        customers = []
        for c in page_items:
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

                "avatar_updated_at": int(c.avatar_updated_at.timestamp()) if c.avatar_updated_at else 0,
                "avatar": f"/customers/get_customer_avatar/{c.id}/" if c.avatar else None,
                "activated": "active" if c.activated else "inactive",
            })

        return {
            "success": True, 
            "answer": customers, 
            "pagination": {
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_records": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous()
            },
            "error": "the serach of the customer was success"}
    
    except Exception as e:
        return {"success": False, "answer": [], "error": str(e)}
    
def desencrypt_avatar(customer):
    # 2. Leer el archivo encriptado desde el storage

    with customer.avatar.open('rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    
    # 3. Desencriptar
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data

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
            "avatar_updated_at": int(customer.avatar_updated_at.timestamp()) if customer.avatar_updated_at else 0,
            "avatar": f"/customers/get_customer_avatar/{customer.id}/" if customer.avatar else None,
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
