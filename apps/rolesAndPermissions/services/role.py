from core.models import Permit, UserRole, Role
from typing import Dict, Any, List


def get_role_of_the_company(user, name: str = '', page: int = 1, activated: bool = True, limit: int = 20) -> Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "message": "Company is required",
            "answer": [],
            "error": "Company is required"
        }

    # calculate offset
    try:
        page = int(page)
    except:
        return {
            "success": False,
            "message": "The page need be a number",
            "answer": [],
            "error": "The page need be a number"
        }
    
    offset = (max(page, 1) - 1) * limit  

    # base queryset
    queryset = UserRole.objects.filter(id_company=company)

    # filtro por nombre
    if name.strip():
        queryset = queryset.filter(name__icontains=name)

    # filtro por estado (activado / desactivado)
    if activated is not None:
        queryset = queryset.filter(activated=activated)

    total = queryset.count()  # total unpaginated results

    roles = queryset.order_by("id")[offset:offset + limit]

    # convertimos resultados
    roles_data: List[Dict[str, Any]] = [
        {
            "id": role.id,
            "name": role.name,
            "text": role.name,
            "description": role.description,
            "creation_date": role.creation_date,
            "activated": role.activated,
        }
        for role in roles
    ]

    return {
        "success": True,
        "message": "Success",
        "error": "Success",
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit,  # total pages rounded up
        "answer": roles_data,
    }

def save_a_new_role(user, data: dict) -> dict:
    name_role = data.get("name_role", "").strip()
    description = data.get("description", "").strip()

    #first we will see if the user add the name of the rol
    if not name_role:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.the-name-is-need",
            "error": "The name of the role is required"
        }

    try:
        #see if alredy exist this name of the rol in the company
        if UserRole.objects.filter(id_company=user.company, name=name_role).exists():
            return {
                "success": False,
                "answer": "rolesAndPermissions.message.error.role-already-exist",
                "error": f"The role '{name_role}' already exists for this company"
            }

        #create a new rol
        role = UserRole.objects.create(
            id_company=user.company,
            name=name_role,
            description=description
        )

        # Exclude keys that are not permissions
        exclude_keys = {"rol_id", "name_role", "description", "rol_id","csrfmiddlewaretoken"}

        # Browse the other fields as permissions
        for key, value in data.items():
            if key in exclude_keys:
                continue

            if value == "on": 
                permit, created = Permit.objects.get_or_create(
                    code=key,
                    defaults={"app": "default", "description": ""}
                )
                Role.objects.create(
                    role=role,
                    permit=permit,
                    active=True
                )

        return {
            "success": True,
            "answer": f"rolesAndPermissions.message.success.this-role-was-create-with-success",
            "error": f"Role '{name_role}' created successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.unexpected-error",
            "error": str(e)
        }
    
def duplicate_role(role_id, company_id):
    try:
        # 1️⃣ get the rol origin of the company
        original_role = UserRole.objects.get(id=role_id, id_company_id=company_id)

        # 2️⃣ create the copy of the rol
        new_role = UserRole.objects.create(
            id_company=original_role.id_company,
            name=f"{original_role.name} - copy",
            description=original_role.description,
            activated=original_role.activated
        )

        # 3️⃣ Duplicate all permissions of the original role
        original_permissions = Role.objects.filter(role=original_role)
        new_roles = [
            Role(role=new_role, permit=rp.permit, active=rp.active)
            for rp in original_permissions
        ]
        Role.objects.bulk_create(new_roles)

        #is very important that return the id of the new rol 
        return {
            "success": True,
            "role_id": new_role.id,
            "message": new_role.id,
            "error": f"Role duplicate with success: {new_role.name}",
        }

    except UserRole.DoesNotExist:
        #if not exist the rol in this company
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.role-id-required",
            "error": "The Role not exist in this company"
        }

    except Exception as e:
        return {
            "success": False,
            "message": "rolesAndPermissions.message.error.unexpected-error",
            "error": str(e)
        }
    
def update_rol_by_id(user, data: dict) -> dict:
    rol_id = data.get("rol_id")
    name_role = data.get("name_role", "").strip()
    description = data.get("description", "").strip()

    if not rol_id:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.role-id-required",
            "error": "Role ID is required"
        }

    try:
        #Find the user's role in the company
        user_role = UserRole.objects.filter(id_company=user.company, id=rol_id).first()
        if not user_role:
            return {
                "success": False,
                "answer": "rolesAndPermissions.message.error.role-not-found",
                "error": f"Role with id {rol_id} not found for this company"
            }

        # Update name and description if submitted
        if name_role:
            user_role.name = name_role
        if description:
            user_role.description = description
        user_role.save()

        # Step 1: Disable all role permissions
        Role.objects.filter(role=user_role).update(active=False)

        # Step 2: Reactivate only sent permissions
        exclude_keys = {"rol_id", "name_role", "description", "rol_id","csrfmiddlewaretoken"}
        for key, value in data.items():
            if key in exclude_keys:
                continue

            if value == "on":
                permit, _ = Permit.objects.get_or_create(
                    code=key,
                    defaults={"app": "default", "description": ""}
                )

                # Find if the relationship already exists
                role_perm, created = Role.objects.get_or_create(
                    role=user_role,
                    permit=permit,
                    defaults={"active": True}
                )
                if not created:  #if it already existed, we just reactivated it
                    role_perm.active = True
                    role_perm.save()

        return {
            "success": True,
            "answer": "rolesAndPermissions.message.success.the-rol-was-update-with-success",
            "error": f"Role '{user_role.name}' updated successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.unexpected-error",
            "error": str(e)
        }

def change_status_of_a_role(user, role_id, status) -> dict:
    if not role_id:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.role-id-required",
            "error": "Role ID is required"
        }

    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.company-is-required",
            "error": "Company is required"
        }
    

    try:
        # search the rol of the company
        user_role = UserRole.objects.filter(id_company=company, id=role_id).first()
        if not user_role:
            return {
                "success": False,
                "answer": "rolesAndPermissions.message.error.role-not-found",
                "error": f"Role with id '{role_id}' not found for this company"
            }

        # desactivate the rol
        user_role.activated = status
        user_role.save()

        # desactivate all the permissions of this rol
        #Role.objects.filter(role=user_role).update(active=status)

        return {
            "success": True,
            "answer": "rolesAndPermissions.message.success.the-rol-was-deactivated",
            "error": f"Role '{user_role.name}' was deactivated successfully"
        }

    except Exception as e:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.unexpected-error",
            "error": str(e)
        }

def get_role_by_id(user, role_id: int) -> Dict[str, Any]:
    if not role_id:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.role-id-required",
            "error": "Role ID is required"
        }
    
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.company-is-required",
            "error": "Company is required"
        }

    try:
        role = UserRole.objects.get(id=role_id, id_company=company)

        # Traer los permisos asociados a este rol
        role_permits = Role.objects.filter(role=role).select_related("permit")

        permits_data: List[Dict[str, Any]] = [
            {
                "id": rp.permit.id,
                "code": rp.permit.code,
                "app": rp.permit.app,
                "description": rp.permit.description,
                "active": rp.active,
            }
            for rp in role_permits
        ]

        role_data = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "creation_date": role.creation_date,
            "activated": role.activated,
            "permits": permits_data,
        }

        return {
            "success": True,
            "answer": role_data,
            "error": "Success"
        }

    except UserRole.DoesNotExist:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.role-not-found",
            "error": f"Role with id {role_id} not found in this company"
        }

    except Exception as e:
        return {
            "success": False,
            "answer": "rolesAndPermissions.message.error.unexpected-error",
            "error": str(e)
        }