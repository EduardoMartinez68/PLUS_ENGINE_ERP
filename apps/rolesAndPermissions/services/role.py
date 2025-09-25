from core.models import Permit, UserRole, Role

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

