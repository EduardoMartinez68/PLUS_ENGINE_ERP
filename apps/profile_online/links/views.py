from django.shortcuts import render
from ..plus_wrapper import Plus
from django.http import JsonResponse
import json 

def profile_online_home(request):
    return render(request, 'home_profile_online.html')


from ..services.profile import get_information_of_the_profile, update_profile_online
def get_information_of_profile_online(request):
    if request.method != 'GET': 
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'view_profile_online'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        ) 

    result=get_information_of_the_profile(request.user) 
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)


def view_update_profile_online(request):
    if request.method != 'POST': 
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'update_profile_online'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        ) 

    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
            status=400
        )   
        
    result=update_profile_online(request.user, data) 
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)


from ..services.services import add_services, update_services
def view_add_services(request):
    if request.method != 'POST': 
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'add_services_profile_online'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )

    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
            status=400
        )   
        
    result=add_services(request.user, data) 
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)



def view_update_services(request, service_id):
    if request.method != 'POST': 
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'add_services_profile_online'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )

    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
            status=400
        )   
        
    result=update_services(request.user, service_id, data) 
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

 
 
 
