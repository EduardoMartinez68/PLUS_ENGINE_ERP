#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from apps.employees.services.branch import get_information_of_the_branch
from apps.employees.services.employees import get_employees_for_search
from ..services.employees import save_employee
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
def add_employee(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse(
                    {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                    status=400
                )   
            
            #now we will see if the user have the permsssion need that the ERP need
            if not Plus.this_user_have_this_permission(request.user, 'add_employee'):
                return JsonResponse(
                    {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                    status=200
                )
            
            result=save_employee(request.user.company,request.user.branch,data)
    
            return JsonResponse({
                "success": result['success'],
                "message": result['message'],
                "error": result['error']
            }, status=200) 
        
    
    
    
    
    
    
    
        
        return render(request, 'add_employee.html')
    else:
        if request.method == "POST":
            try:
                data = json.loads(request.body)
            except Exception as e:
                return JsonResponse(
                    {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                    status=400
                )   
            
            #now we will see if the user have the permsssion need that the ERP need
            if not Plus.this_user_have_this_permission(request.user, 'add_employee'):
                return JsonResponse(
                    {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                    status=200
                )
            
            result=save_employee(request.user.company,request.user.branch,data)
    
            return JsonResponse({
                "success": result['success'],
                "message": result['message'],
                "error": result['error']
            }, status=200) 
        
    
    
    
    
    
    
    
        
        return render(request, 'add_employee.html')

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
    
    
        all_filters = request.GET.get("allFilters", "")
        values = all_filters.split(",")
        search=values[0]
        branch_name = values[1].strip() if values[1] and values[1].strip() else request.user.branch
        some_flag = values[2] if values[2] not in (None, "") else True
    
        result = get_employees_for_search(
            company=request.user.company,
            branch= branch_name,
            sku=search,
            activated=some_flag
        )
    
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
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
    
    
        all_filters = request.GET.get("allFilters", "")
        values = all_filters.split(",")
        search=values[0]
        branch_name = values[1].strip() if values[1] and values[1].strip() else request.user.branch
        some_flag = values[2] if values[2] not in (None, "") else True
    
        result = get_employees_for_search(
            company=request.user.company,
            branch= branch_name,
            sku=search,
            activated=some_flag
        )
    
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

@login_required(login_url='login')
def search_branch(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'view_employee_of_all_the_branch'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            search = request.GET.get("query")
            result = get_information_of_the_branch(
                company=request.user.company,
                name=search
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
        if not Plus.this_user_have_this_permission(request.user, 'view_employee_of_all_the_branch'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            search = request.GET.get("query")
            result = get_information_of_the_branch(
                company=request.user.company,
                name=search
            )
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

