#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from apps.employees.services.employees import get_employees_for_search
from ..plus_wrapper import Plus
import json
from django.http import JsonResponse
from django.shortcuts import render
@login_required(login_url='login')
def employees_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_employees.html')
    else:
        return render(request, 'home_employees.html')

@login_required(login_url='login')
def search_employee(request, activated):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'view_employee'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
    
    
        try:
            search = request.GET.get("query")
            result = get_employees_for_search(
                company=request.user.company,
                branch=request.user.branch,
                sku=search,
                activated=activated
            )
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 
    else:
        if request.method == "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'view_employee'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
    
    
        try:
            search = request.GET.get("query")
            result = get_employees_for_search(
                company=request.user.company,
                branch=request.user.branch,
                sku=search,
                activated=activated
            )
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

