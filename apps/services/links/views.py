from django.shortcuts import render
from ..plus_wrapper import Plus
import json
from django.http import JsonResponse

def services_home(request):
    return render(request, 'services/home.html')

#------------------------------------------------------------------SERVICES----------------------------------------------
from apps.services.services.Pack import PackService
def search_pack(request, activate):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    

    try:
        allFilters = request.GET.get("allFilters", "")
        data=allFilters.split(",")
        key = data[0] if len(data) > 0 else ""
        page = request.GET.get("page", 1)
        amountOfData = request.GET.get("amountOfData", 20)

        result = PackService.search(request.user, key, page, Plus.to_bool(activate), amountOfData)

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
        
def add_services(request):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'add_products'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        try:
            data = json.loads(request.body)
            result = PackService.add(request.user, data)
            return JsonResponse({
                "success": result.get('success',False),
                "message": result.get('message',''),
                "error": result.get('error','')
            }, status=200) 
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)


    return render(request, 'services/form.html')

def update_services(request):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'update_products'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        try:
            data = json.loads(request.body)
            can_update_prices=Plus.this_user_have_this_permission(request.user, 'update_product_price')
            result = PackService.update(request.user, data, can_update_prices)
            return JsonResponse({
                "success": result.get('success',False),
                "message": result.get('message',''),
                "error": result.get('error','')
            }, status=200) 
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)
        
def delete_services(request, services_id):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'delete_products'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        try:
            data = json.loads(request.body)
            data['activated'] = False
            can_update_prices = False
            result = PackService.update(request.user, data, can_update_prices)
            return JsonResponse({
                "success": result.get('success',False),
                "message": result.get('message',''),
                "error": result.get('error','')
            }, status=200) 
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)

def restart_services(request, services_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'restore_products'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    try:
        result = PackService.activate(request.user, services_id)

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
    
def get_information_product(request, product_id):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    try:
        result = PackService.get_information_by_id(request.user, product_id)

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

#------------------------------------------------------------------TAXES----------------------------------------------
from apps.services.services.tax import TaxService
def search_tax(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
     
    try:
        query = request.GET.get("query", "").strip()
        result = TaxService.search(request.user, query, 1)

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
    
def add_tax(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'manage_product_taxes'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:
        data = json.loads(request.body)
        result = TaxService.add(request.user, data)
        return JsonResponse({
            "success": result.get('success',False),
            "message": result.get('message',''),
            "error": result.get('error','')
        }, status=200) 
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400)

def get_information_tax(request, tax_id):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'manage_product_taxes'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:
        result = TaxService.get_tax(request.user, tax_id)
        return JsonResponse({
            "success": result.get('success',False),
            "answer": result.get('answer',{}),
            "message": result.get('message',''),
            "error": result.get('error','')
        }, status=200) 
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400)
    
def update_tax(request, tax_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'manage_product_taxes'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )

    try:
        data = json.loads(request.body)
        result = TaxService.update(request.user, data)
        return JsonResponse({
            "success": result.get('success',False),
            "answer": result.get('answer',{}),
            "message": result.get('message',''),
            "error": result.get('error','')
        }, status=200) 
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400)
    
#------------------------------------------------------------------DEPARTAMENTS----------------------------------------------
from apps.services.services.departament import Departaments
def search_departament(request):
    # Ensure request method is GET
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    try:
        query = request.GET.get("query", "").strip()
        result = Departaments.search(request.user, query, 1)

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
        
def add_departament(request):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'manage_product_categories'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
            
        try:
            data = json.loads(request.body)
            result = Departaments.add(request.user, data)
            return JsonResponse({
                "success": result.get('success',False),
                "message": result.get('message',''),
                "error": result.get('error','')
            }, status=200) 
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)
        
def update_departament(request, departament_id):
    if request.method == "POST":

        if not Plus.this_user_have_this_permission(request.user, 'manage_product_categories'):
            return JsonResponse({
                "success": False,
                "message": 'message.this-user-not-have-this-permission',
                "error": 'this user not have this permission'
            }, status=200)

        try:
            data = json.loads(request.body)
            result = Departaments.update(request.user, data)

            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "error": result.get('error', ''),
                "data": result.get('data', {})
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)

def delete_departament(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    

    if not Plus.this_user_have_this_permission(request.user, 'manage_product_categories'):
        return JsonResponse({
            "success": False,
            "message": 'message.this-user-not-have-this-permission',
            "error": 'this user not have this permission'
        }, status=200)

    try:
        data = json.loads(request.body)

        # Force logical deletion
        data['activated'] = False

        result = Departaments.update(request.user, data)

        return JsonResponse({
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "error": result.get('error', ''),
            "data": result.get('data', {})
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400)

def get_information_departament(request, departament_id):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    try:
        result = Departaments.get_information_by_id(request.user, departament_id)

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
     
#------------------------------------------------------------------CATEGORY----------------------------------------------
from apps.services.services.category import Category
def search_category(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    try:
        query = request.GET.get("query", "").strip()
        page = 1

        result = Category.search(request.user, query, page)
        return JsonResponse({
            "success": result.get('success', False),
            "answer": result.get('answer', []),
            "message": result.get('message', ''),
            "error": result.get('error', ''),
            "data": result.get('data', {})
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400)
        
def add_category(request):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'manage_product_categories'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
            
        try:
            data = json.loads(request.body)
            result = Category.add(request.user, data)
            return JsonResponse({
                "success": result.get('success',False),
                "message": result.get('message',''),
                "error": result.get('error','')
            }, status=200) 
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)
        
def update_category(request, category_id):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'manage_product_categories'):
            return JsonResponse({
                "success": False,
                "message": 'message.this-user-not-have-this-permission',
                "error": 'this user not have this permission'
            }, status=200)

        try:
            data = json.loads(request.body)

            result = Category.update(request.user, data)

            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "error": result.get('error', ''),
                "data": result.get('data', {})
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)

def delete_category(request):
    if request.method == "POST":
        if not Plus.this_user_have_this_permission(request.user, 'manage_product_categories'):
            return JsonResponse({
                "success": False,
                "message": 'message.this-user-not-have-this-permission',
                "error": 'this user not have this permission'
            }, status=200)

        try:
            data = json.loads(request.body)

            # Force logical deletion
            data['activated'] = False

            result = Category.update(request.user, data)

            return JsonResponse({
                "success": result.get('success', False),
                "message": result.get('message', ''),
                "error": result.get('error', ''),
                "data": result.get('data', {})
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "message": "message.invalid-json",
                "error": "Invalid JSON"
            }, status=400)
        
def get_information_category(request, category_id):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    try:
        result = Category.get_information_by_id(request.user, category_id)

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
   