#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from apps.departament_employee.services.department import search_department_for_filter
from django.http import JsonResponse
from django.shortcuts import render
@login_required(login_url='login')
def departament_employee_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_departament_employee.html')
    else:
        return render(request, 'home_departament_employee.html')

@login_required(login_url='login')
def search_employee_department(request, activated):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
    else:
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

