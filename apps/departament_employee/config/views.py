#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from apps.departament_employee.services.employee import search_users_in_company
from apps.departament_employee.services.department import search_department_for_filter, get_data_of_the_departament_by_id, add_new_department, delete_departament_by_id, update_departament
import json
from django.http import JsonResponse
from django.shortcuts import render
@login_required(login_url='login')
def departament_employee_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'departament_employee/home_departament_employee.html')
    else:
        return render(request, 'departament_employee/home_departament_employee.html')

@login_required(login_url='login')
def search_employee_department(request, activated):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)
    
        try:
            search = request.GET.get("query")
            result = search_department_for_filter(
                user=request.user,
                search=search,
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
        if request.method != "GET":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)
    
        try:
            search = request.GET.get("query")
            result = search_department_for_filter(
                user=request.user,
                search=search,
                activated=activated
            )
    
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

@login_required(login_url='login')
def get_information_of_the_departament(request, departament_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405) 
        
        try:
            result = get_data_of_the_departament_by_id(request.user, departament_id)
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 
    else:
        if request.method != "GET":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405) 
        
        try:
            result = get_data_of_the_departament_by_id(request.user, departament_id)
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

@login_required(login_url='login')
def add_new_departament(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST": 
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405) 
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=add_new_department(request.user, data)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    else:
        if request.method != "POST": 
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405) 
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
            
        result=add_new_department(request.user, data)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

@login_required(login_url='login')
def edit_departament(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        try:
            result = update_departament(request.user, data)
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 
    else:
        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        try:
            result = update_departament(request.user, data)
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

@login_required(login_url='login')
def delete_departament(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        try:
            result = delete_departament_by_id(request.user, data['id'])
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 
    else:
        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405)  
        
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        try:
            result = delete_departament_by_id(request.user, data['id'])
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

@login_required(login_url='login')
def search_employee(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405) 
        
        try:
            # --- parámetros que vienen por query string ---
            search = request.GET.get("query", "")
            # --- ejecutar la búsqueda ---
            result = search_users_in_company(request.user,search)
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 
    else:
        if request.method != "GET":
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": "Method not allowed."
            }, status=405) 
        
        try:
            # --- parámetros que vienen por query string ---
            search = request.GET.get("query", "")
            # --- ejecutar la búsqueda ---
            result = search_users_in_company(request.user,search)
            return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "answer": [],
                "error": str(e)
            }, status=500) 

