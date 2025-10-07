from django.db.models import Q
from ..plus_wrapper import Plus
from core.models import UserDepartment
from django.core.exceptions import ValidationError
from core.models import CustomUser

def search_department_for_filter(user, search=None, activated=None, limit=20):
    try:
        # --- 1. limit first to the user's company ---
        company = getattr(user, "company", None)
        qs = UserDepartment.objects.filter(id_company=company)

        # --- 2. filter by activated ---
        qs = qs.filter(activated=Plus.to_bool(activated))


        # --- 3. apply search filter ---
        if search and search.strip():
            qs = qs.filter(
                Q(name__icontains=search.strip())
            )

        # --- 4. limit results ---
        qs = qs.order_by("name")[:limit]

        # --- 5. format the response ---
        departments = []
        for d in qs:
            manager_data = {
                "id": '',
                "name": '',
                "photo": '/static/img/employees-select.webp'         
            }

            if hasattr(d, "manager") and d.manager:  #only if exist the data of the manager we will to save it
                manager_data = {
                    "id": d.manager.id,
                    "name": d.manager.username,
                    "photo": d.manager.avatar.url if d.manager.avatar else '/static/img/employees-select.webp',
                }

            departments.append({
                "id": d.id,
                "name": d.name,
                "text": d.name,
                "description": d.description or "",
                "color": d.color or "#085DA9",
                "activated": "active" if d.activated else "inactive",
                "manager_id": manager_data['id'],
                "manager_name": manager_data['name'],
                "manager_photo": manager_data['photo'],
                "employees_count": d.customuser_set.filter(is_active=True).count() #the number of employees that exist in this departament
            })

        return {"success": True, "answer": departments, "error": None}

    except Exception as e:
        return {"success": False, "answer": [], "error": str(e)}

def get_data_of_the_departament_by_id(user, departament_id):
    try:
        company = getattr(user, "company", None)
        if not company:
            return {"success": False, "answer": 'departament_employee.error.this-user-not-have-a-company', "error": "The user no have a company"}

        #search the departament for the departament id and the user company
        d = UserDepartment.objects.filter(
            id=departament_id,
            id_company=company
        ).first()

        if not d:
            return {"success": False, "answer": None, "error": "This departament not exist in this company"}

        #save the data of the manager
        manager_data = None
        if hasattr(d, "manager") and d.manager:
            manager_data = {
                "id": d.manager.id,
                "name": d.manager.username,
                "photo": d.manager.avatar.url if d.manager.avatar else None,
            }

        # Formatear respuesta
        department_data = {
            "id": d.id,
            "name": d.name,
            "description": d.description or "",
            "color": d.color or "#085DA9",
            "activated": "active" if d.activated else "inactive",
            "manager": manager_data,
        }

        return {"success": True, "answer": department_data, "error": None}

    except Exception as e:
        return {"success": False, "answer": None, "error": str(e)}
    
def add_new_department(user, data):
    try:
        # 1. here we will see if the user have a company save
        company = getattr(user, "company", None)
        if not company:
            return {"success": False, "answer": 'departament_employee.error.this-user-not-have-a-company', "error": "This user not have a company"}

        # 2. get the data in style JSON
        name = data.get("name-departament")
        description = data.get("description-departament")
        color = data.get("color-departament") or "#085DA9"
        activated = data.get("activated", True)
        id_manager = data.get("id_manager")

        # 3. we will see if can save the information or the user need other data for save
        if not name or name.strip() == "":
            return {"success": False, "answer": 'departament_employee.error.the-departament-need-name', "error": "The name of the departament is required"}
        
        # 4. check if the manager exists in the company
        manager_instance = None
        if id_manager:
            try:
                manager_instance = CustomUser.objects.get(id=id_manager, company=company)
            except CustomUser.DoesNotExist:
                return {"success": False, "answer": 'departament_employee.error.the-manager-not-exit', "error": "The manager not exist in this company."}
            

        # 5. Avoid duplicates in the same company
        if UserDepartment.objects.filter(name__iexact=name.strip(), id_company=company).exists():
            return {"success": False, "answer": 'departament_employee.error.this-departament-is-already-in-this-company', "error": "This department is already in this company."}

        # 6. create the departament
        department = UserDepartment.objects.create(
            name=name.strip(),
            description=description or "",
            color=color,
            id_company=company,
            activated=activated,
            manager=manager_instance
        )

        # 7. return the answer of the backend
        return {
            "success": True,
            "answer": {
                "id": department.id,
                "name": department.name,
                "description": department.description,
                "color": department.color,
                "activated": "active" if department.activated else "inactive",
                "manager": {
                    "id": department.manager.id if department.manager else None,
                    "name": str(department.manager) if department.manager else None
                }
            },
            "error": None
        }

    except ValidationError as ve:
        return {"success": False, "answer": 'departament_employee.error.error-in-the-server', "error": str(ve)}

    except Exception as e:
        return {"success": False, "answer": 'departament_employee.error.error-in-the-server', "error": str(e)}
    
def update_departament(user, data):
    try:
        # 1. Verificar que el usuario tenga compañía
        company = getattr(user, "company", None)
        if not company:
            return {"success": False, "answer": 'departament_employee.error.this-user-not-have-a-company', "error": "This user not have a company."}

        # 2. Obtener los datos del formulario
        departament_id = data.get("departament_id")
        name = data.get("edit-name-departament")
        description = data.get("edit-description-departament")
        color = data.get("edit-color-departament") or "#085DA9"
        activated = data.get("activated", True)
        id_manager = data.get("edit-id_manager")

        if not departament_id:
            return {"success": False, "answer": 'departament_employee.error.department-id-required', "error": "we need the id of the departament"}

        # 3. Buscar el departamento
        try:
            department = UserDepartment.objects.get(id=departament_id, id_company=company)
        except UserDepartment.DoesNotExist:
            return {"success": False, "answer": 'departament_employee.error.department-not-found', "error": "This departament not exist in this company"}

        # 4. Validar el nombre
        if not name or name.strip() == "":
            return {"success": False, "answer": 'departament_employee.error.the-departament-need-name', "error": "You need add the name of the departament"}

        # 5. Validar duplicados de nombre en la compañía (excepto el mismo departamento)
        if UserDepartment.objects.filter(name__iexact=name.strip(), id_company=company).exclude(id=departament_id).exists():
            return {"success": False, "answer": 'departament_employee.error.this-departament-is-already-in-this-company', "error": "This departament already exist in this company"}

        # 6. Validar el manager
        manager_instance = None
        if id_manager:
            try:
                id_manager=int(id_manager)
                manager_instance = CustomUser.objects.get(id=id_manager, company=company)
            except CustomUser.DoesNotExist:
                return {"success": False, "answer": 'departament_employee.error.the-manager-not-exit', "error": "This manager not exist in this company"}

        # 7. Actualizar los campos
        department.name = name.strip()
        department.description = description or ""
        department.color = color
        department.activated = activated
        department.manager = manager_instance
        department.save()

        # 8. Retornar la respuesta
        return {
            "success": True,
            "answer": {
                "id": department.id,
                "name": department.name,
                "description": department.description,
                "color": department.color,
                "activated": "active" if department.activated else "inactive"
            },
            "error": None
        }

    except ValidationError as ve:
        return {"success": False, "answer": 'departament_employee.error.error-in-the-server', "error": str(ve)}

    except Exception as e:
        return {"success": False, "answer": 'departament_employee.error.error-in-the-server', "error": str(e)}


def delete_departament_by_id(user, departament_id):
    try:
        # 1. Verificar que el usuario tenga compañía
        company = getattr(user, "company", None)
        if not company:
            return {"success": False, "answer": 'departament_employee.error.this-user-not-have-a-company', "error": "The user not have a company"}

        # 2. Intentar obtener el departamento dentro de la compañía
        try:
            department = UserDepartment.objects.get(id=departament_id, id_company=company)
        except UserDepartment.DoesNotExist:
            return {"success": False, "answer": 'departament_employee.error.department-not-found', "error": "El departamento no existe en esta compañía."}

        # 3. Eliminar el departamento
        department.delete()

        # 4. Retornar éxito
        return {
            "success": True,
            "answer": f"The departament '{department.name}' was delete with success",
            "error": f"The departament '{department.name}' was delete with success."
        }

    except Exception as e:
        return {"success": False, "answer": 'departament_employee.error.error-in-the-server', "error": str(e)}