from django.shortcuts import render
from ..plus_wrapper import Plus
from django.http import JsonResponse
import json

from ..services.schedule import get_branch_schedule_all
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

    #here we will see if have permission for edit the schedule for get from the function
    schedule=None
    if permissions.get("edit_schedule"):
        schedule=get_branch_schedule_all(branch)

    from django.conf import settings
    facebook_id=settings.FB_APP_ID
    facebook_redirect_uri=f'https://{settings.PLUS_URL}/setting/whatsapp_callback'
    return render(request, 'setting/home_setting.html', {"user": user, "company": company, "branch":branch, "permissions": permissions, "schedule": schedule, "facebook_id":facebook_id, "facebook_redirect_uri":facebook_redirect_uri})




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



from ..services.user import update_user, update_slug_user
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



def view_update_schedule(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
            status=400
        )  
        
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'edit_schedule'):
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
       
    
    from ..services.schedule import save_branch_schedule
    result=save_branch_schedule(request.user.branch, data) 

    return JsonResponse({
        "success": result['success'],
        "answer": result['answer'],
        "message": result['message'],
        "error": result.get('error',"")
    }, status=200)   



#/setting/whatsapp_callback
def whatsapp_callback(request):
    import requests
    from django.conf import settings
    from django.shortcuts import redirect
    from django.utils import timezone
    from core.models import WhatsAppAccount

    code = request.GET.get("code")

    if not code:
        return redirect("/setting/setting_home/?error=no_code")

    # 1. Swap "code" for "access_token"
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    params = {
        "client_id": settings.FB_APP_ID,
        "client_secret": settings.FB_APP_SECRET,
        "redirect_uri": f"https://{settings.PLUS_URL}:8000/setting/whatsapp_callback/",
        "code": code,
    }

    token_res = requests.get(token_url, params=params)
    token_data = token_res.json()

    if "access_token" not in token_data:
        return redirect("/setting_home/?error=token_error")

    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 3600)  # 1 hora por defecto
    token_expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)

    # 2. Get the connected business info: waba_id, phone_number_id, display_phone_number
    me_url = (
        "https://graph.facebook.com/v18.0/me?"
        "fields=id,name,accounts{business,phone_numbers}"
        f"&access_token={access_token}"
    )

    me_res = requests.get(me_url)
    me_data = me_res.json()

    try:
        account = me_data["accounts"]["data"][0]
    except:
        return redirect("/setting/setting_home/")

    waba_id = account["id"]

    try:
        phone_info = account["phone_numbers"]["data"][0]
    except:
        return redirect("/setting/setting_home/")

    phone_number_id = phone_info["id"]
    display_phone_number = phone_info["display_phone_number"]

    # 3. Save or update record in database
    WhatsAppAccount.objects.update_or_create(
        company=request.user.company,
        branch=request.user.branch,
        defaults={
            "access_token": access_token,
            "token_expires_at": token_expires_at,
            "waba_id": waba_id,
            "phone_number_id": phone_number_id,
            "display_phone_number": display_phone_number,
            "status": "connected",
        }
    )

    # 4. Redirect the user
    return redirect("/setting/setting_home/")



def view_update_profile_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
            status=400
        )  
        
    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse(
            {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
            status=400
        )
    
    result=update_slug_user(request.user, data)
    return JsonResponse({
        "success": result.get('success',False),
        "answer": result.get('answer',''),
        "message": result.get('message',''),
        "error": result.get('error',"")
    }, status=200)   