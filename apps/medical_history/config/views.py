#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.medical import get_information_medical_in_list
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

