from core.models import Permit, UserRole, Role
from typing import Dict, Any, List


def get_role_of_the_company(company, name: str = '', page: int = 1, limit: int = 20) -> Dict[str, Any]:
    if not company:
        return {"success": False, "message": "Company is required", "answer": [], "error": "Company is required"}

    # calculate offset
    try:
        page=int(page)
    except:
        return {"success": False, "message": "The page need be a number", "answer": [], "error": "The page need be a number"}
    
    offset = (max(page, 1) - 1) * limit  

    # base queryset
    queryset = UserRole.objects.filter(id_company=company)

    if name.strip():
        queryset = queryset.filter(name__icontains=name)

    total = queryset.count()  # total unpaginated results

    roles = queryset.order_by("id")[offset:offset + limit]

    # we convert results
    roles_data: List[Dict[str, Any]] = [
        {
            "id": role.id,
            "name": role.name,
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

def save_a_new_role(user, data:dict)->dict:
    #here we will see if exist the name of the rol 
    name_role=data.get("name_role", "").strip()
    description=data.get("description", "").strip()

    if name_role=='':
        return {"success": False, "answer": "rolesAndPermissions.message.error.the-name-is-need" ,"error": "Customer updated successfully"}
    
    try:
        role = UserRole.objects.create(
            id_company=user.company,
            name=name_role,
            description=description
        )

        #this inputs not are permissions
        exclude_keys = {"name_role", "description", "csrfmiddlewaretoken"}


        # 4. Recorrer todas las demás claves como permisos
        for key in data.keys():
            if key in exclude_keys:
                continue

            # Si viene marcado (checkbox o similar)
            if data.get(key) == "on":
                permit, created = Permit.objects.get_or_create(
                    code=key,
                    defaults={"app": "default", "description": ""}
                )
                Role.objects.create(
                    role=new_role,
                    permit=permit,
                    active=True
                )


    except:
        pass 

