#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.inventory.services.inventory import InventoryService
from django.http import JsonResponse
import json
from core.Plus import Plus
from httpcore import request
from django.shortcuts import render
@login_required(login_url='login')
def inventory_home(request):
        return render(request, 'inventory/home.html')

@login_required(login_url='login')
def get_data_inventory(request, pack_id):
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_products'):
            return JsonResponse(
                {
                    "success": False,
                    "answer": 'message.this-user-not-have-this-permission',
                    "error": 'this user not have this permission'
                },
                status=200
            ) 
        
    
        result = InventoryService.get_information_by_id(request.user,pack_id)
    
        return JsonResponse({
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "answer": result.get('answer', []),
            "error": result.get('error', ''),
            "pagination": result.get('pagination', {})
        }, status=200)

@login_required(login_url='login')
def get_inventory(request):
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_products'):
            return JsonResponse(
                {
                    "success": False,
                    "answer": 'message.this-user-not-have-this-permission',
                    "error": 'this user not have this permission'
                },
                status=200
            )
    
        try:
            allFilters = request.GET.get("allFilters", "")
            page = request.GET.get("page", 1)
            filters = allFilters.split(",")
    
            key = filters[0] if len(filters) > 0 and filters[0] else None
            status = filters[1] if len(filters) > 1 and filters[1] else None
            if status == "all":
                status = None
            else:
                try:
                    status=int(status)
                except:
                    pass
    
            result = InventoryService.search_with_inventory(
                user=request.user,
                key=key,
                page=page,
                status=status
            )
    
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except Exception as e:
            return JsonResponse({
                "success": False,
                "message": "message.server-error",
                "error": str(e)
            }, status=500)

@login_required(login_url='login')
def update_inventory(request):
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'update_inventory'):
            return JsonResponse(
                {
                    "success": False,
                    "answer": 'message.this-user-not-have-this-permission',
                    "error": 'this user not have this permission'
                },
                status=200
            )
    
        try:
            data = json.loads(request.body)
            result = InventoryService.update_inventory(request.user, data.get("id", None), data.get('new_exist', 0))
    
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "data": result.get('data', {})
            }, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)

@login_required(login_url='login')
def get_history_inventory(request):
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            allFilters = request.GET.get("allFilters", "")
            page = request.GET.get("page", 1)
            filters = allFilters.split(",")
    
            key = filters[0] if len(filters) > 0 and filters[0] else None
    
            date_start = filters[1] if len(filters) > 1 and filters[1] else None
            date_finish = filters[2] if len(filters) > 2 and filters[2] else None
            pack_id = filters[3] if len(filters) > 3 and filters[3] else None
            user_id = filters[4] if len(filters) > 4 and filters[4] else None
    
            result = InventoryService.get_history_inventory(
                request.user,
                request.user.branch,
                page,
                date_start,
                date_finish,
                pack_id,
                user_id
            )
    
    
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except Exception as e:
            print(e)
            return JsonResponse({
                "success": False,
                "message": "message.server-error",
                "error": str(e)
            }, status=500)

