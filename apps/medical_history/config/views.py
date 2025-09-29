#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.medical import get_information_medical_in_list, get_information_of_the_medical_history_for_customer_id
from django.template.loader import render_to_string
import json
from ..plus_wrapper import Plus
from django.http import JsonResponse
from django.shortcuts import render
@login_required(login_url='login')
def medical_history_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_medical_history.html')
    else:
        return render(request, 'home_medical_history.html')

@login_required(login_url='login')
def get_list_of_medical_history(request, page):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET': 
            skull = request.GET.get("skull")
            result = get_information_medical_in_list(request.user, skull, page)
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
        
    
        return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)
    else:
        if request.method == 'GET': 
            skull = request.GET.get("skull")
            result = get_information_medical_in_list(request.user, skull, page)
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
        
    
        return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

@login_required(login_url='login')
def medical_history(request, customer_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        result = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
        if result["success"]:
            # Renderizamos el HTML como string
            html = render_to_string("form_medical_history.html", {"data": result["answer"]}, request=request)
            return JsonResponse({"success": True, "html": html})
        else:
            return JsonResponse({"success": False, "error": result.get("error", "Unknown error")})
    else:
        result = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
        if result["success"]:
            # Renderizamos el HTML como string
            html = render_to_string("form_medical_history.html", {"data": result["answer"]}, request=request)
            return JsonResponse({"success": True, "html": html})
        else:
            return JsonResponse({"success": False, "error": result.get("error", "Unknown error")})

@login_required(login_url='login')
def get_medical_history_with_customer_id(request, customer_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'GET': 
            result = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
        
    
        return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)
    else:
        if request.method == 'GET': 
            result = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
        
    
        return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

