#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.odontogram import get_odontograms, add_new_odontogram, get_latest_history_for_odontogram, update_tooth
from django.template.loader import render_to_string
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from ..plus_wrapper import Plus
from django.shortcuts import render
@login_required(login_url='login')
def odontograma_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_odontograma.html')
    else:
        return render(request, 'home_odontograma.html')

@login_required(login_url='login')
def search_odontogram(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

@login_required(login_url='login')
def add_odontogram(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET': 
            return render(request, 'load_form_odontograma.html')
        
        #this is when the user would like add a new odotogram
        elif request.method == 'POST': 
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
    else:
        if request.method == 'GET': 
            return render(request, 'load_form_odontograma.html')
        
        #this is when the user would like add a new odotogram
        elif request.method == 'POST': 
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

@login_required(login_url='login')
def view_odontogram(request, odontogram_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET': 
            context = {
                "odontogram_id": odontogram_id
            }
    
            return render(request, 'odontogram.html', context)
    else:
        if request.method == 'GET': 
            context = {
                "odontogram_id": odontogram_id
            }
    
            return render(request, 'odontogram.html', context)

@login_required(login_url='login')
def get_information_of_the_odotngoram(request, odontogram_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_latest_history_for_odontogram(request.user, odontogram_id)
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)
    else:
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_latest_history_for_odontogram(request.user, odontogram_id)
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)

@login_required(login_url='login')
def view_update_tooth(request, odontogram_id, tooth_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )  
            
        result = update_tooth(tooth_id, odontogram_id, data, request.user)
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)
    else:
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )  
            
        result = update_tooth(tooth_id, odontogram_id, data, request.user)
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)

