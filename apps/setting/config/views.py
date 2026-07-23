#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.setting.models import NotificationSetting, NotificationSettingUser, CustomUser
from ..services.billingData import update_branch_billing_data, get_branch_billing_data
from ..services.user import update_user, update_slug_user
from ..services.branch import update_branch, update_token_branch
from ..services.company import update_company
from ..services.branch import get_whatsapp_credentials, get_branches
from ..services.schedule import get_branch_schedule_all
import os 
import json
from django.http import JsonResponse
from core.Plus import Plus
from core.settings import BASE_DIR
from django.shortcuts import render
@login_required(login_url='login')
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
        company.company_logo_url=company.logo.url if company.logo else ""
      
        #here we will to construct the permissions that have the user in the view of the settings 
        permissions=Plus.get_user_permissions(user, 
        ["edit_system","edit_company", 
         "edit_branch", "edit_drivers", 
         "edit_schedule", "edit_email", 
         "edit_data_facture", 
         "edit_data_whatsapp_bussiness",
         "edit_notification"
         ]
        ) 
    
        #here we will see if have permission for edit the schedule for get from the function
        schedule=None
        if permissions.get("edit_schedule"):
            schedule=get_branch_schedule_all(branch)
    
        from django.conf import settings
        facebook_id=settings.FB_APP_ID
        facebook_redirect_uri=f'https://{settings.PLUS_URL}/setting/whatsapp_callback'
    
    
        whatsapp_account=get_whatsapp_credentials(request.user)
        return render(request, 'setting/home_setting.html', {"user": user, "company": company, "branch":branch, "permissions": permissions, "schedule": schedule, "facebook_id":facebook_id, "facebook_redirect_uri":facebook_redirect_uri, "whatsapp_account":whatsapp_account})

@login_required(login_url='login')
def search_branches(request):
        if request.method != "GET":
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": "method not success"}, 
                status=400
            )  
        
        try:
            result = get_branches(request.user, request.GET.get("search", None))
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Error fetching branches", "error": str(e)},
                status=200
            )
    
        return JsonResponse({
            "success": True,
            "message": "",
            "error": "",
            "answer": results
        }, status=200)

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def save_token_whatsapp(request):
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
    
        result=update_token_branch(request.user,data)
        return JsonResponse({
            "success": result.get('success',False),
            "answer": result.get('answer',''),
            "message": result.get('message',''),
            "error": result.get('error',"")
        }, status=200)  

@login_required(login_url='login')
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

@login_required(login_url='login')
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

@login_required(login_url='login')
def get_user_notification(request, slug):
        type_notification=slug
    
        if request.method != 'GET':
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed"
            }, status=405)
    
        try:
    
            notification = NotificationSetting.objects.prefetch_related(
                'users__user'
            ).get(
                company=request.user.company,
                branch=request.user.branch,
                type_notification=type_notification
            )
    
        except NotificationSetting.DoesNotExist:
    
            return JsonResponse({
                "success": True,
                "answer": [],
                "error": ""
            }, status=200)
    
        users = []
    
        for relation in notification.users.all():
    
            users.append({
                "id": relation.user.id
            })
    
        return JsonResponse({
            "success": True,
            "answer": users,
            "error": ""
        }, status=200)

@login_required(login_url='login')
def save_user_notification(request, slug):
        type_notification=slug
        try:
    
            body = json.loads(request.body)
    
            users_ids = body.get('users', [])
    
            # create or get notification
            notification, created = NotificationSetting.objects.get_or_create(
                company=request.user.company,
                branch=request.user.branch,
                type_notification=type_notification,
                defaults={
                    "notify_by_email": True,
                    "notify_by_system": True
                }
            )
    
            # delete old users
            NotificationSettingUser.objects.filter(
                notification=notification
            ).delete()
    
            # get valid users
            users = CustomUser.objects.filter(
                company=request.user.company,
                branch=request.user.branch,
                id__in=users_ids
            )
    
            # create relations
            relations = []
    
            for user in users:
    
                relations.append(
                    NotificationSettingUser(
                        notification=notification,
                        user=user
                    )
                )
    
            NotificationSettingUser.objects.bulk_create(relations)
    
            return JsonResponse({
                "success": True,
                "answer": "Users saved successfully",
                "error": ""
            })
    
        except Exception as e:
    
            return JsonResponse({
                "success": False,
                "answer": "",
                "error": str(e)
            }, status=500)

@login_required(login_url='login')
def save_notification_setting(request, slug):
    
        if request.method != 'POST':
    
            return JsonResponse({
                "success": False,
                "answer": "",
                "error": "Method not allowed"
            }, status=405)
    
        try:
    
            body = json.loads(request.body)
    
            send_for_email = Plus.to_bool(body.get('send_for_email',False))
            send_for_system =  Plus.to_bool(body.get('send_for_system',False))
    
            notification, created = (
                NotificationSetting.objects.update_or_create(
    
                    company=request.user.company,
                    branch=request.user.branch,
                    type_notification=slug,
    
                    defaults={
                        "notify_by_email": send_for_email,
                        "notify_by_system": send_for_system
                    }
                )
            )
    
            return JsonResponse({
    
                "success": True,
    
                "answer": {
                    "id": notification.id,
                    "type_notification": notification.type_notification,
                    "notify_by_email": notification.notify_by_email,
                    "notify_by_system": notification.notify_by_system,
                    "created": created
                },
    
                "error": ""
    
            })
    
        except Exception as e:
    
            return JsonResponse({
    
                "success": False,
                "answer": "",
                "error": str(e)
    
            }, status=500)

@login_required(login_url='login')
def get_all_notification_settings(request):
    
        try:
    
            notifications = NotificationSetting.objects.filter(
                company=request.user.company
            ).values(
                'id',
                'type_notification',
                'notify_by_email',
                'notify_by_system',
                'branch_id'
            )
    
            return JsonResponse({
                "success": True,
                "answer": list(notifications),
                "error": ""
            })
    
        except Exception as e:
    
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500)

