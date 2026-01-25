from ..plus_wrapper import Plus
from core.models import CustomUser, Company, Branch, UserDepartment, UserRole
from django.core.paginator import Paginator
from django.db.models import Q

import base64, uuid, hashlib, traceback
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.db import transaction
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from datetime import datetime, date
import hashlib

def get_employees_for_search(company, branch=None, sku=None, activated=None, page=1, limit=20) -> dict:
    """
    Get employees filtered by company, branch, username search, and activation status.
    Returns paginated results including decrypted email, phone, and cellphone.
    """

    query = CustomUser.objects.filter(company=company)

    if branch:
        query = query.filter(branch=branch)

    if activated is not None:
        query = query.filter(is_active=Plus.to_bool(activated))

    # Solo búsqueda por username
    if sku:
        query = query.filter(username__icontains=sku)

    # Cargar relaciones relacionadas
    query = query.select_related("user_role", "user_department", "branch")

    # Ordenar por nombre real
    query = query.order_by("name", "username")

    paginator = Paginator(query, limit)
    employees_page = paginator.get_page(page)

    results = []
    for emp in employees_page:
        results.append({
            "id": emp.id,
            "avatar": emp.avatar.url if emp.avatar else "/static/img/profile-employees.webp",
            "name": emp.name or "",
            "username": emp.username or "",
            "email": emp.email or "",
            "cellphone": emp.cellphone or "",
            "phone": emp.phone or "",
            "branch": emp.branch.name_branch if emp.branch else "",
            "department": emp.user_department.name if emp.user_department else "",
            "department_color": emp.user_department.color if emp.user_department and emp.user_department.color else "#075FAC",
            "role": emp.user_role.name if emp.user_role else "",
            "is_active": emp.is_active,
        })

    return {
        "success": True,
        "answer": results,
        "page": employees_page.number,
        "total_pages": paginator.num_pages,
        "total_employees": paginator.count,
        "error": "",
    }

def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def valid_the_form_of_employee(company, branch, data , employee_id=None):
    # --- See if the branch exist in the company ---
    if branch.company_id != company.id:
        return {"success": False, "message":"employees.error.this-branch-not-exit","error": "The branch does not belong to the provided company."}

    # --- basic inputs ---
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    username = data.get("username") or name or email
    password1 = (data.get("password") or "").strip()
    password2 = (data.get("confirm-password") or "").strip()

    #we will see if exist the name and the password are equals
    if not name:
        return {"success": False, "message":"employees.message.the-name-is-need" ,"error": "Name is required for employee creation."}
            
    #we will see if exist the fields obligatory
    if not email:
        return {"success": False, "message":"employees.message.the-email-is-need" ,"error": "Email is required for employee creation."}
    
    #we will see if the user need eval the password that send the user front the frontend, if not need do, is because the user is editing a employee
    if employee_id==None:
        if password1!=password2 or password1=='':
            return {"success": False, "message":"employees.message.the-password-is-need" ,"error": "Tha password not are equals"} 
        
        #here we will see if the email already exist in the system
        if employee_id==None:
            if CustomUser.objects.filter(email=email).exists():
                return {"success": False, "message":"employees.message.email-exist", "error": "Email already registered."}
        else:
            if CustomUser.objects.filter(email=email).exclude(id=employee_id).exists():
                return {"success": False, "message":"employees.message.email-exist", "error": "Email already registered."}


    return {"success":True}
        
def save_employee(company: Company, branch: Branch, data: dict)->list:
    """
    Create a new employee in the company and branch specific.
    Verify that the branch belongs to the company before creating the employee.
    """

    #we will see if the form that send the frontend is success or need other data
    result=valid_the_form_of_employee(company, branch, data)
    if not result["success"]:
        return {"success": False, "message":result["message"], "error": result["error"]} 
    

    try:
        # --- basic inputs ---
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        username = data.get("username") or name or email
        password1 = (data.get("password") or "").strip()

        #now if exist all the field of the form and the email is valid, now we will to create to employee
        with transaction.atomic():
            employee = CustomUser()

            employee.company = company
            employee.branch = branch
            employee.username = username

            # --- SAVE THE BASIC INFORMATION ---
            employee.name = name
            employee.email = email
            employee.address = data.get("address", "")
            employee.phone = data.get("phone", "")
            employee.cellphone = data.get("cellphone", "")

            #get the birth and if not is of type date, we will to save a null
            dob = data.get("date_of_birth")
            if isinstance(dob, (datetime, date)):
                employee.date_of_birth = dob if isinstance(dob, date) else dob.date()
            else:
                try:
                    employee.date_of_birth = datetime.strptime(str(dob), "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    employee.date_of_birth = None

            employee.set_password(password1)

            # --- OTHER OPTIONS ---
            employee.language = data.get("language", "es")
            employee.timezone = data.get("timezone", "America/Mexico_City")
            employee.country = data.get("country", "MX")
            employee.postal_code = data.get("postal_code", "")

            # --- ROLE AND DEPARTAMENTS (only if exist) ---
            role_id = data.get("user_role")
            employee.user_role = UserRole.objects.filter(id=role_id).first() if role_id else None

            dept_id = data.get("user_department")
            employee.user_department = UserDepartment.objects.filter(id=dept_id).first() if dept_id else None

            # --- date of hiring ---
            employee.hiring_date = data.get("hiring_date") or None

            # --- PROCESAR AVATAR (base64 opcional) ---
            avatar_data = data.get("avatar")
            if avatar_data and "," in avatar_data:
                try:
                    fmt, imgstr = avatar_data.split(",", 1)
                    img_data = base64.b64decode(imgstr)
                    img = Image.open(BytesIO(img_data))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    # Redimensionar
                    max_size = (400, 400)
                    img.thumbnail(max_size, Image.LANCZOS)

                    # Guardar en WebP
                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=85)
                    buffer.seek(0)

                    unique_filename = f"{uuid.uuid4().hex}_avatar.webp"
                    employee.avatar.save(unique_filename, ContentFile(buffer.read()), save=False)
                except Exception as e:
                    print("Error processing avatar:", e)

            employee.is_active = data.get("is_active", True)
            employee.is_staff = data.get("is_staff", False)
            # --- save employee ---
            employee.save()

            return {
                "success": True,
                "message": f"Employee '{name}' created successfully.",
                "employee_id": employee.id,
                "error":""
            }

    except ValidationError as e:
        return {"success": False, "message":"employees.message.we-not-can-add-this-employee","error": str(e)}
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "message":"employees.message.we-not-can-add-this-employee", "error": str(e)}
    
def update_employee(company: Company, branch: Branch, employee_id:int ,data: dict)->list:
    """
    Create a new employee in the company and branch specific.
    Verify that the branch belongs to the company before creating the employee.
    """
    #first we will see if exist a employee id 
    if employee_id is None:
        return {"success": False, "message":result["message"], "error": "Need send the id of the employee"} 
    
    #we will see if the form that send the frontend is success or need other data
    result=valid_the_form_of_employee(company, branch, data, employee_id)
    if not result["success"]:
        return {"success": False, "message":result["message"], "error": result["error"]} 
    

    try:
        # --- basic inputs ---
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip().lower()
        username = data.get("username") or name or email

        #now if exist all the field of the form we will get the user object use the his id
        employee = CustomUser.objects.get(id=employee_id, company=company)

        #employee.company = company
        #employee.branch = branch
        employee.username = username

        # --- SAVE THE BASIC INFORMATION ---
        employee.name = name
        employee.email = email
        employee.address = data.get("address", "")
        employee.phone = data.get("phone", "")
        employee.cellphone = data.get("cellphone", "")

        #we will to try save of birth of the employee
        dob = data.get("date_of_birth")
        if isinstance(dob, (datetime, date)):
            employee.date_of_birth = dob if isinstance(dob, date) else dob.date()
        else:
            try:
                employee.date_of_birth = datetime.strptime(str(dob), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                employee.date_of_birth = None

        
        # --- OTHER OPTIONS ---
        employee.language = data.get("language", "es")
        employee.timezone = data.get("timezone", "America/Mexico_City")
        employee.country = data.get("country", "MX")
        employee.postal_code = data.get("postal_code", "")

        # --- ROLE AND DEPARTAMENTS (only if exist) ---
        role_id = data.get("user_role")
        employee.user_role = UserRole.objects.filter(id=role_id).first() if role_id else None

        dept_id = data.get("user_department")
        employee.user_department = UserDepartment.objects.filter(id=dept_id).first() if dept_id else None

        # --- date of hiring ---
        employee.hiring_date = data.get("hiring_date") or None

        # --- PROCESAR AVATAR (base64 opcional) ---
        avatar_data = data.get("avatar")
        if avatar_data:
            # Si el usuario envía una cadena base64 (nuevo avatar)
            if "," in avatar_data:
                try:
                    fmt, imgstr = avatar_data.split(",", 1)
                    img_data = base64.b64decode(imgstr)
                    img = Image.open(BytesIO(img_data))
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGB")

                    # Redimensionar
                    max_size = (400, 400)
                    img.thumbnail(max_size, Image.LANCZOS)

                    # Guardar en WebP
                    buffer = BytesIO()
                    img.save(buffer, format="WEBP", quality=85)
                    buffer.seek(0)

                    # Si ya tenía un avatar previo, eliminarlo
                    if employee.avatar:
                        employee.avatar.delete(save=False)

                    unique_filename = f"{uuid.uuid4().hex}_avatar.webp"
                    employee.avatar.save(unique_filename, ContentFile(buffer.read()), save=False)
                except Exception as e:
                    print("Error processing avatar:", e)

            # Si el frontend envía un string vacío => borrar avatar existente
            elif avatar_data == "":
                if employee.avatar:
                    employee.avatar.delete(save=False)
                    employee.avatar = None
        else:
            #if we have a phone in the server but the user delete the image of the employee, we will to delete 
            if employee.avatar:
                employee.avatar.delete(save=False) 
                employee.avatar = None

        employee.is_active = data.get("is_active", True)
        employee.is_staff = data.get("is_staff", False)
        # --- save employee ---
        employee.save()

        return {
            "success": True,
            "message": f"Employee '{name}' update successfully.",
            "employee_id": employee.id,
            "error":""
        }

    except ValidationError as e:
        return {"success": False, "message":"employees.message.we-not-can-update-this-employee","error": str(e)}
    except Exception as e:
        traceback.print_exc()
        return {"success": False, "message":"employees.message.we-not-can-update-this-employee", "error": str(e)}
    
def change_employee_status(company: Company, employee_id: int, new_status: bool) -> dict:
    """
    Change the active status of an employee (activate or deactivate).
    Parameters:
        company (Company): The company that owns the employee.
        employee_id (int): The ID of the employee whose status will be changed.
        new_status (bool): True to activate, False to deactivate.
    Returns:
        dict: Result of the operation with success flag and message.
    """
    try:
        #we will see if the id that send is valid
        if not employee_id:
            return {
                "success": False,
                "message": "employees.error.this-employee-not-exist",
                "error": "invalid_id"
            }

        # try get the employee in the company
        employee = CustomUser.objects.filter(id=employee_id, company=company).first()
        if not employee:
            return {
                "success": False,
                "message": "employees.error.this-employee-not-exist",
                "error": "employee not found"
            }

        # update his status
        employee.is_active = new_status

        #now we will see if the employee have a photo, if have a photo we will to delete
        if not new_status and employee.avatar:
            try:
                employee.avatar.delete(save=False)
                employee.avatar = None
            except Exception as e:
                print(f"Error deleting avatar for employee {employee.id}: {e}")

        # save the change
        employee.save()

        #return the answer
        status_text = "activated" if new_status else "deactivated"
        return {
            "success": True,
            "message": f"Employee '{employee.name}' was {status_text} successfully.",
            "employee_id": employee.id,
            "new_status": new_status,
            "error": f"Employee '{employee.name}' was {status_text} successfully."
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "message": "An error occurred while changing the employee status.",
            "error": str(e)
        }


def get_information_of_employee_by_id(company: Company, employee_id: int) -> dict:
    """
    Obtiene la información de un empleado filtrando por la empresa.
    Esto asegura que un usuario solo pueda ver empleados de su compañía.
    """
    try:
        # Filtrar empleado por ID y por empresa
        employee = CustomUser.objects.select_related(
            'company', 'branch', 'user_role', 'user_department'
        ).get(id=employee_id, company=company)

        # Preparar la información a devolver
        employee_data = {
            "id": employee.id,
            "name": employee.name,
            "username": employee.username,
            "email": employee.email,
            "avatar": employee.avatar.url if employee.avatar else None,
            "address": employee.address,
            "country": employee.country,
            "postal_code": employee.postal_code,
            "date_of_birth": employee.date_of_birth.isoformat() if employee.date_of_birth else None,
            "hiring_date": employee.hiring_date.isoformat() if employee.hiring_date else None,
            "cellphone": employee.cellphone,
            "phone": employee.phone,
            "timezone": employee.timezone,
            "language": employee.language,
            "is_active": employee.is_active,
            "is_staff": employee.is_staff,
            # --- Branch info ---
            "branch": {
                "id": employee.branch.id if employee.branch else None,
                "name": employee.branch.name_branch if employee.branch else None,
                "email": employee.branch.email_branch if employee.branch else None
            } if employee.branch else None,
            # --- Role info ---
            "user_role": {
                "id": employee.user_role.id if employee.user_role else None,
                "name": employee.user_role.name if employee.user_role else None
            } if employee.user_role else None,
            # --- Department info ---
            "user_department": {
                "id": employee.user_department.id if employee.user_department else None,
                "name": employee.user_department.name if employee.user_department else None,
                "color": employee.user_department.color if employee.user_department else '#1649FF'
            } if employee.user_department else None,
            "color_departament": employee.user_department.color if employee.user_department else '#1649FF'
        }

        return {"success": True, "employee": employee_data, "error": ""}
    
    except ObjectDoesNotExist:
        return {"success": False, "employee": None, "error": "Employee not found or does not belong to your company."}
    except Exception as e:
        return {"success": False, "employee": None, "error": str(e)}