#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.odontogram import get_odontograms
from django.http import JsonResponse
from ..plus_wrapper import Plus
from django.shortcuts import render
@login_required(login_url='login')
def odontograma_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_odontograma.html')
    else:
        return render(request, 'home_odontograma.html')

@login_required(login_url='login')
def search_odontogram(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_odontogram'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
    
        search = request.GET.get("query", "") 
        result=get_odontograms(request.user, search) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)
    else:
        if request.method != 'GET': 
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_odontogram'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            ) 
    
    
        search = request.GET.get("query", "") 
        result=get_odontograms(request.user, search) 
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)

@login_required(login_url='login')
def add_odontogram(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'load_form_odontograma.html')
    else:
        return render(request, 'load_form_odontograma.html')

@login_required(login_url='login')
def get_odontogram(request, odontogram_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_odontograma.html')
    else:
        return render(request, 'home_odontograma.html')

