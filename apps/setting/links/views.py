from django.shortcuts import render
from ..plus_wrapper import Plus
from django.http import JsonResponse
import json

def setting_home(request):
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
    permissions=Plus.get_user_permissions(user, ["edit_system","edit_company", "edit_branch", "edit_drivers", "edit_schedule", "edit_email", "edit_data_facture"]) 

    return render(request, 'home_setting.html', {"user": user, "company": company, "branch":branch, "permissions": permissions})




from ..services.company import update_company
def view_update_company(request):
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




from ..services.branch import update_branch
def view_update_branch(request):
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



from ..services.user import update_user
def view_update_setting_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
            status=400
        )  
        
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'edit_setting_user'):
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
    result=update_user(request.user, data) 

    return JsonResponse({
        "success": result['success'],
        "message": result['message'],
        "error": result.get('error',"")
    }, status=200)  



from ..services.billingData import update_branch_billing_data, get_branch_billing_data
def view_update_data_facture_branch(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
            status=400
        )  
        
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'edit_data_facture'):
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
    result=update_branch_billing_data(request.user.branch, data) 

    return JsonResponse({
        "success": result['success'],
        "message": result['message'],
        "error": result.get('error',"")
    }, status=200)  


def view_get_branch_billing_data(request):
    if request.method != "GET":
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
            status=400
        )  
        
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'edit_data_facture'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    #here we will to construct the permissions that have the user in the view of the settings 
    result=get_branch_billing_data(request.user.branch) 
 
    return JsonResponse({
        "success": result['success'],
        "answer": result['answer'],
        "message": result['message'],
        "error": result.get('error',"")
    }, status=200)   