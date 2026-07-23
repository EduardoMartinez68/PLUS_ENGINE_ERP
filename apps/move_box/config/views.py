#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.move_box.services.move_box import Move
from django.http import JsonResponse
import json
from core.Plus import Plus
from httpcore import request
from django.shortcuts import render
@login_required(login_url='login')
def move_box_home(request):
        return render(request, 'move_box/home.html')

@login_required(login_url='login')
def save_move(request):
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_move_box'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Move.do_a_move(request.user, data)
    
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
def search_move(request):
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_move_box'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            user=request.user
            allFilters = request.GET.get("allFilters", "")
            page = request.GET.get("page", 1)
    
            # 🔥 Parsear filtros correctamente
            filters = allFilters.split(",")
    
            key = filters[0] if len(filters) > 0 and filters[0] else None
            branch_id = filters[1] if len(filters) > 1 and filters[1] else None
            branch_id=None
            user_id = filters[2] if len(filters) > 2 and filters[2] else None
            date_start = filters[3] if len(filters) > 3 and filters[3] else None
            date_end = filters[4] if len(filters) > 4 and filters[4] else None
            method = filters[5] if len(filters) > 5 and filters[5] else None
            if method == "all":
                method = None
    
            result = Move.search_by_comment(user, key, page, branch_id, user_id,date_start, date_end,method)
    
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "pagination": result.get('pagination', []),
                "error": result.get('error', ''),
                "data": result.get('data', {})
            }, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400) 

