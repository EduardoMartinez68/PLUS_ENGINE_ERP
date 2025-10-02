from django.shortcuts import render
from django.http import JsonResponse

def departament_employee_home(request):
    return render(request, 'home_departament_employee.html')



from apps.departament_employee.services.department import search_department_for_filter
def search_employee_department(request, activated):
    if request.method != "GET":
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": "Método no permitido. Usa GET."
        }, status=405)

    try:
        # --- parámetros que vienen por query string ---
        search = request.GET.get("search")

        # --- ejecutar la búsqueda ---
        result = search_department_for_filter(
            user=request.user,
            search=search,
            activated=activated
        )

        return JsonResponse(result, safe=False, status=200)

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
            "error": "Método no permitido. Usa GET."
        }, status=405) 
    
    try:
        # --- parámetros que vienen por query string ---
        search = request.GET.get("query", "")
        # --- ejecutar la búsqueda ---
        result = search_users_in_company(request.user,search)
        print(result)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

    except Exception as e:
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": str(e)
        }, status=500) 