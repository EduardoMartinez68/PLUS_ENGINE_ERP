from django.http import JsonResponse
from django.shortcuts import render
import json
from apps.rolesAndPermissions.services.permits import get_all_the_permissions
from apps.rolesAndPermissions.services.role import get_role_of_the_company
from ..plus_wrapper import Plus
from django.shortcuts import redirect

def rolesAndPermissions_home(request):
    return render(request, 'rolesAndPermissions/home_rolesAndPermissions.html')

def get_information_of_the_role(request, activated):
    if request.method == "GET": 
        name = request.GET.get("query", "")
        page = request.GET.get("page", 1)
        activated = Plus.to_bool(activated)

        answer = get_role_of_the_company(request.user, name=name, page=page, activated=activated)
        return JsonResponse(answer, status=200)

    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

def get_all_the_permissions_of_the_erp(request):
    if request.method == "GET": 
        '''
        get all the permissions that exist in this ERP. Not need a company id or a user id because
        the permissions be load from the apps of the ERP not from a company or a user
        '''
        permissions = get_all_the_permissions()
        return JsonResponse({'success': True, 'answer': permissions}, status=200)




from apps.rolesAndPermissions.services.role import save_a_new_role, get_role_by_id, update_rol_by_id, change_status_of_a_role, duplicate_role
def add_a_new_rol(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )        

        result=save_a_new_role(request.user, data)
        if result.get("success"):
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)

    elif request.method == "GET":
        return render(request, 'rolesAndPermissions/form_rol.html')
    

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

def edit_rol(request, rol_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )        
        
        result=update_rol_by_id(request.user, data)
        if result.get("success"):
            return JsonResponse(result, status=200)
        else:
            return JsonResponse(result, status=400)

    elif request.method == "GET":
        return render(request, 'rolesAndPermissions/form_rol.html', {
            "role": {"rol_id": rol_id} 
        })
        

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

def duplicate_rol_in_the_company(request, rol_id):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'duplicate_role'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        #if the user have the permission of duplicate a role, we will do that
        result=duplicate_role(rol_id, request.user.company.id)
        #we will see if we can duplicate the role
        return JsonResponse({
            "success": result['success'],
            "answer": result['message'],
            "error": result['error']
        }, status=200) 

        

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)


def get_information_rol(request, rol_id):
    if request.method == "GET":
        result = get_role_by_id(request.user, rol_id)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)
        

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

def change_status(request):
    if request.method == "POST":
        body_json = json.loads(request.body)

        #if the frontend send the <role_id> is because the user is in the app update the information of the rol
        #else if the frontend send <id> is because the user is editing the rol from a select
        role_id = body_json.get("role_id") or body_json.get("id") or "" 
        status = Plus.to_bool(body_json.get("status"))
        result = change_status_of_a_role(request.user, role_id, status)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)