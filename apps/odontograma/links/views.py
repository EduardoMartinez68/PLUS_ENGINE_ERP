from django.shortcuts import render
from ..plus_wrapper import Plus
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.template.loader import render_to_string

def odontograma_home(request):
    return render(request, 'home_odontograma.html')



from ..services.odontogram import get_odontograms, add_new_odontogram, get_latest_history_for_odontogram, update_tooth
def search_odontogram(request):
    if request.method != 'GET': 
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'view_odontogram'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        ) 


    search = request.GET.get("query", "") 
    result=get_odontograms(request.user, search) 
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

def add_odontogram(request):
    if request.method == 'GET': 
        return render(request, 'load_form_odontograma.html')
    
    #this is when the user would like add a new odotogram
    elif request.method == 'POST': 
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'add_odontogram'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        #get the information of the form
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        result=add_new_odontogram(request.user, data) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("odontogram_id", ''), 'error':result.get("error", 'not exist error in the return')}, status=200)



def view_odontogram(request, odontogram_id):
    if request.method == 'GET': 
        context = {
            "odontogram_id": odontogram_id
        }

        return render(request, 'odontogram.html', context)

def get_information_of_the_odotngoram(request, odontogram_id):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'view_odontogram'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
        
    result = get_latest_history_for_odontogram(request.user, odontogram_id)
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)

def view_update_tooth(request, odontogram_id, tooth_id):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'update_odontogram'):
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
        
    result = update_tooth(tooth_id, odontogram_id, data, request.user)
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)


def update_periodontogram(request, periodontogram_id):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'update_odontogram'):
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
        
    from ..services.periodontogram import update_periodontogram_service
    result = update_periodontogram_service(periodontogram_id, data, request.user)
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)


def view_setting(request):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    return render(request, 'odontogram_setting.html')