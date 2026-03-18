#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from apps.sales.services.sales import Sales
from django.http import JsonResponse
import json
from ..plus_wrapper import Plus
from django.shortcuts import render
@login_required(login_url='login')
def sales_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'sales/home.html')
    else:
        return render(request, 'sales/home.html')

@login_required(login_url='login')
def get_the_sales(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
            
    
        view_sales_totals=Plus.this_user_have_this_permission(request.user, 'view_sales_totals')
    
        try:
            key = request.GET.get("query", "")
            page = request.GET.get("page", 1)
            result = Sales.search(request.user, key, page, view_sales_totals)
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)
    else:
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
            
    
        view_sales_totals=Plus.this_user_have_this_permission(request.user, 'view_sales_totals')
    
        try:
            key = request.GET.get("query", "")
            page = request.GET.get("page", 1)
            result = Sales.search(request.user, key, page, view_sales_totals)
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)

@login_required(login_url='login')
def add_sale(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not Plus.this_user_have_this_permission(request.user, 'add_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
            
        if request.method == "GET":
            context = {
                "company": request.user.company if hasattr(request.user, "company") else None,
                "branch": request.user.branch if hasattr(request.user, "branch") else None,
            }
            return render(request, 'sales/addSales.html', context)
    
        #when the user do a method post is because the user want to save the sale, so we will save the sale and return a json response with the result of the operation
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            data = json.loads(request.body)
            result = Sales.add(request.user, data)
    
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
    else:
        if not Plus.this_user_have_this_permission(request.user, 'add_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
            
        if request.method == "GET":
            context = {
                "company": request.user.company if hasattr(request.user, "company") else None,
                "branch": request.user.branch if hasattr(request.user, "branch") else None,
            }
            return render(request, 'sales/addSales.html', context)
    
        #when the user do a method post is because the user want to save the sale, so we will save the sale and return a json response with the result of the operation
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
        try:
            data = json.loads(request.body)
            result = Sales.add(request.user, data)
    
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
def update_sale(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'edit_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Sales.update_status(request.user, data.get("id"), data.get("status"))
    
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
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'edit_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Sales.update_status(request.user, data.get("id"), data.get("status"))
    
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
def view_sale(request, sale_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        context = {
            "company": request.user.company if hasattr(request.user, "company") else None,
            "branch": request.user.branch if hasattr(request.user, "branch") else None,
        }
        return render(request, 'sales/view_sale.html', {"sale_id": sale_id, **context})
    else:
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        context = {
            "company": request.user.company if hasattr(request.user, "company") else None,
            "branch": request.user.branch if hasattr(request.user, "branch") else None,
        }
        return render(request, 'sales/view_sale.html', {"sale_id": sale_id, **context})

@login_required(login_url='login')
def get_sale_info(request, sale_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            result = Sales.get_sale_info(request.user, sale_id)
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
    else:
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            result = Sales.get_sale_info(request.user, sale_id)
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
def get_sale_history(request, sale_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            page = request.GET.get("page", 1)
            per_page = request.GET.get("per_page", 10)
            result = Sales.get_sale_history(request.user, sale_id, page, per_page)
    
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "data": result.get('data', {}),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)
    else:
        if request.method != "GET":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            page = request.GET.get("page", 1)
            per_page = request.GET.get("per_page", 10)
            result = Sales.get_sale_history(request.user, sale_id, page, per_page)
    
            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "answer": result.get('answer', []),
                "error": result.get('error', ''),
                "data": result.get('data', {}),
                "pagination": result.get('pagination', {})
            }, status=200)
    
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)

@login_required(login_url='login')
def do_a_sale(request, sale_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Sales.do_a_sale(request.user, sale_id, data)
    
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
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'add_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Sales.do_a_sale(request.user, sale_id, data)
    
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
def cancel_sale(request, sale_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'cancel_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Sales.cancel_sale(request.user, sale_id, data)
    
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
    else:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
        
        if not Plus.this_user_have_this_permission(request.user, 'cancel_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            result = Sales.cancel_sale(request.user, sale_id, data)
    
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
def send_buy_email(request, sale_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            email = data.get("email")
            result=Sales.send_sale_email(request.user, sale_id, email)
    
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
    else:
        try:
            data = json.loads(request.body)
            email = data.get("email")
            result=Sales.send_sale_email(request.user, sale_id, email)
    
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

