from django.shortcuts import render
import json
from django.shortcuts import render
from django.http import JsonResponse
from core.plus.services import ServiceRegistry

def payroll_home(request):
    return render(request, 'payroll/home.html')


def create_employee_contract(request):
    if request.method == "GET":
        return render(request, "payroll/employee_contract_form.html")
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "answer": "message.invalid-json",
                "error": "El cuerpo de la petición no es un JSON válido"
            }, status=400)

        #run the service
        return ServiceRegistry.execute(
            "payroll.EmployeeContractService.create_employee_contract", 
            request.user, 
            data
        )

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405) 
