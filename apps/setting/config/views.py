#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.branch import update_branch
from ..services.company import update_company
import json
from django.http import JsonResponse
from ..plus_wrapper import Plus
from django.shortcuts import render
@login_required(login_url='login')
def setting_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
            
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'view_settings'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        user=request.user
        company = user.company
        branch = user.branch
    
        #here we will to construct the permissions that have the user in the view of the settings 
        permissions=Plus.get_user_permissions(user, ["edit_system","edit_company", "edit_branch", "edit_drivers", "edit_schedule", "edit_email"]) 
    
        return render(request, 'home_setting.html', {"company": company, "branch":branch, "permissions": permissions})
    else:
        if request.method != "GET":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
            
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'view_settings'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        user=request.user
        company = user.company
        branch = user.branch
    
        #here we will to construct the permissions that have the user in the view of the settings 
        permissions=Plus.get_user_permissions(user, ["edit_system","edit_company", "edit_branch", "edit_drivers", "edit_schedule", "edit_email"]) 
    
        return render(request, 'home_setting.html', {"company": company, "branch":branch, "permissions": permissions})

@login_required(login_url='login')
def view_update_company(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
            
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'edit_company'):
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
    
    
        #here we will to construct the permissions that have the user in the view of the settings 
        result=update_company(request.user, data) 
    
        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result.get('error',"")
        }, status=200) 
    else:
        if request.method != "POST":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
            
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'edit_company'):
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
    
    
        #here we will to construct the permissions that have the user in the view of the settings 
        result=update_company(request.user, data) 
    
        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result.get('error',"")
        }, status=200) 

@login_required(login_url='login')
def view_update_branch(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
            
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'edit_branch'):
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
    
    
        #here we will to construct the permissions that have the user in the view of the settings 
        result=update_branch(request.user, data) 
    
        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result.get('error',"")
        }, status=200) 
    else:
        if request.method != "POST":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
            
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'edit_branch'):
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
    
    
        #here we will to construct the permissions that have the user in the view of the settings 
        result=update_branch(request.user, data) 
    
        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result.get('error',"")
        }, status=200) 

