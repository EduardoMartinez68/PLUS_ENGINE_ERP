from django.shortcuts import render
from django.http import JsonResponse
import json

def departament_employee_home(request):
    return render(request, 'departament_employee/home_departament_employee.html')



from apps.departament_employee.services.department import search_department_for_filter, get_data_of_the_departament_by_id, add_new_department, delete_departament_by_id, update_departament
def search_employee_department(request, activated):
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
    
def get_information_of_the_departament(request, departament_id):
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

def add_new_departament(request):
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

def edit_departament(request):
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

def delete_departament(request):
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

from apps.departament_employee.services.employee import search_users_in_company
def search_employee(request):
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
    

