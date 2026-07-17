from django.shortcuts import render
from httpcore import request
from ..plus_wrapper import Plus
import json
from django.http import JsonResponse

def sales_home(request):
    return render(request, 'sales/home.html')

from apps.sales.services.sales import Sales
def get_the_sales(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'view_sales'):
        return JsonResponse(
            {
                "success": False,
                "answer": 'message.this-user-not-have-this-permission',
                "error": 'this user not have this permission'
            },
            status=200
        )

    view_sales_totals = Plus.this_user_have_this_permission(request.user, 'view_sales_totals')

    try:
        allFilters = request.GET.get("allFilters", "")
        page = request.GET.get("page", 1)

        # 🔥 Parsear filtros correctamente
        filters = allFilters.split(",")

        key = filters[0] if len(filters) > 0 and filters[0] else None
        customer_id = filters[1] if len(filters) > 1 and filters[1] else None
        user_id = filters[2] if len(filters) > 2 and filters[2] else None
        date_start = filters[3] if len(filters) > 3 and filters[3] else None
        date_end = filters[4] if len(filters) > 4 and filters[4] else None
        status = filters[5] if len(filters) > 5 and filters[5] else None
        if status == "all":
            status = None

        result = Sales.search(
            user=request.user,
            key=key,
            page=page,
            view_sales_totals=view_sales_totals,
            customer_id=customer_id,
            user_id=user_id,
            date_start=date_start,
            date_end=date_end,
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
    
def add_sale(request):
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
    
def update_sale(request):
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

def view_sale(request, sale_id):
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

def get_sale_info(request, sale_id):
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

def get_sale_history(request, sale_id):
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

def do_a_sale(request, sale_id):
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

def cancel_sale(request, sale_id):
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

def send_buy_email(request, sale_id):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        result=Sales.send_sale_email(request.user, sale_id, email)
        print(result)
        
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

def save_signature(request, sale_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'save_signature'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:
        data = json.loads(request.body)
        result = Sales.save_signature(request, request.user, sale_id, data)
        
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
    
def view_upload_excel(request):
    return render(request, 'sales/upload_sale.html')

def download_excel_template(request):
    pass 


from apps.sales.services.excel import upload_excel
@csrf_exempt
def upload_excel_sales(request):
    #we will see if the user send the file by a method POST
    if request.method == 'POST':
        excel_file = request.FILES.get('file')
        if not excel_file:
            return JsonResponse({"success": False, "answer":"sales.error.not-exist-file",'error': 'The user not upload nothing file'}, status=400)

         # 🔒 We verify the size of the file (maximum 5 MB)
        max_size_mb = 5
        max_size_bytes = max_size_mb * 1024 * 1024  # convert to bytes

        #if the size of the file is very big we will return a message of error to the frontend
        if excel_file.size > max_size_bytes:
            return JsonResponse({
                "success": False,
                "answer": "sales.error.file-too-large",
                "error": f"The file exceeds the limit {max_size_mb} MB"
            }, status=400)
        
        #now if the file have the size perfect we will see if can save the information in the database
        if Plus.this_user_have_this_permission(request.user, 'upload_customer_for_excel'):
            answer=upload_excel(request.user, excel_file)
            return JsonResponse(
                {"success": answer.get("success",False), "answer": answer.get("answer",''), "error": answer.get("error",'')},
                status=200
            )
        else:
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
                 
    return JsonResponse(
        {"success": False, "answer": [], "error": ''},
        status=400
    )



@public
def pay_sale(request, slug):
    sale =Sales.get_information_of_link_of_pay(slug)
    return render(request, 'sales/pay_sale.html' , {'sale': sale.get('answer', {})})


