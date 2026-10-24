#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.contract.services.ContractTemplateService import ContractTemplateService
from core.plus.services import ServiceRegistry
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from django.shortcuts import render
@login_required(login_url='login')
def contract_home(request):
        return render(request, 'contract/home.html')

@login_required(login_url='login')
def view_search_contract_templates(request):
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        all_filters = request.GET.get("allFilters", "")
    
        filters = all_filters.split(",")
    
        query = (
            filters[0].strip()
            if filters and filters[0].strip()
            else None
        )
    
        return JsonResponse(
            ServiceRegistry.execute(
                "contracts.ContractTemplateService.search_contract_templates",
                request.user,
                query
            )
        )

@login_required(login_url='login')
def view_create_contract_template(request):
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        try:
            data = json.loads(request.body)
    
            if not isinstance(data, dict):
                return JsonResponse({
                    "success": False,
                    "error": "El cuerpo de la petición debe ser un objeto JSON."
                }, status=400)
    
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({
                "success": False,
                "error": "El JSON enviado no es válido."
            }, status=400)
    
        result = ServiceRegistry.execute(
            "contracts.ContractTemplateService.create_contract_template",
            request.user,
            data
        )
    
        return JsonResponse(result)

@login_required(login_url='login')
def view_update_contract_template(request, template_id):
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        try:
            data = json.loads(request.body)
    
            if not isinstance(data, dict):
                return JsonResponse({
                    "success": False,
                    "error": "El cuerpo de la petición debe ser un objeto JSON."
                }, status=400)
    
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({
                "success": False,
                "error": "El JSON enviado no es válido."
            }, status=400)
    
        result = ServiceRegistry.execute(
            "contracts.ContractTemplateService.update_contract_template",
            request.user,
            template_id,
            data
        )
    
        return JsonResponse(result)

@login_required(login_url='login')
def view_delete_contract_template(request, template_id):
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        result = ServiceRegistry.execute(
            "contracts.ContractTemplateService.delete_contract_template",
            request.user,
            template_id
        )
    
        return JsonResponse(result)

@login_required(login_url='login')
def view_get_contract_template(request, template_id):
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        result = ServiceRegistry.execute(
            "contracts.ContractTemplateService.get_contract_template",
            request.user,
            template_id
        )
    
        return JsonResponse(result)

