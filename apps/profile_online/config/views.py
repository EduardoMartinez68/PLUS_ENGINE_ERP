#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.address import save_profile_location
from ..services.schedule import update_profile_schedule
from ..services.services import add_services, update_services
from ..services.profile import get_information_of_the_profile, update_profile_online
import json 
from django.http import JsonResponse
from ..plus_wrapper import Plus
from django.shortcuts import render
@login_required(login_url='login')
def profile_online_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_profile_online.html')
    else:
        return render(request, 'home_profile_online.html')

@login_required(login_url='login')
def get_information_of_profile_online(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
        result=get_information_of_the_profile(request.user) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_profile_online'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
        result=get_information_of_the_profile(request.user) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_profile_online(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

@login_required(login_url='login')
def view_add_services(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

@login_required(login_url='login')
def view_update_services(request, service_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

@login_required(login_url='login')
def view_update_schedule(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
        result=update_profile_schedule(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
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
    
        result=update_profile_schedule(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def view_update_address(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    
        result=save_profile_location(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
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
    
        result=save_profile_location(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

