from django.shortcuts import render

from core.Plus import Plus
import json
from django.http import JsonResponse

def reports_home(request):
    permissions=Plus.get_user_permissions(request.user, 
    ["watch_reports_sales","watch_reports_inventory", 
     "watch_reports_move_money"]
    ) 

    return render(request, 'reports/home.html', {"permissions": permissions})


from apps.reports.services.payments import ReportsPayments
def search_reports_move(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_move_money'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:
        user = request.user
        json_data_string = next(iter(request.GET.keys()), None)
        page=1
        if json_data_string:
            try:
                filtros = json.loads(json_data_string)
                page = filtros.get('page', 1)
            except json.JSONDecodeError:
                page = 1
        else:
            page = 1
        
        result = ReportsPayments.search_move(
            user=user,
            page= page,
            key= filtros.get('key'),
            branch_id= filtros.get('branch_id'),
            user_id= filtros.get('user_id'),
            method= filtros.get('method'),
            date_start= filtros.get('date_start'),
            date_end= filtros.get('date_end')
        )
        
        return JsonResponse({
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "answer": result.get('answer', []),
            "pagination": result.get('pagination', []),
            "summary": result.get('summary', 0),
            "error": result.get('error', ''),
            "data": result.get('data', {})
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400) 


from apps.reports.services.sales import ReportsSales
def search_reports_sales(request):
    if request.method != "GET":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_sales'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:

        user = request.user

        filtros = {}

        json_data_string = next(
            iter(request.GET.keys()),
            None
        )

        if json_data_string:
            try:
                filtros = json.loads(
                    json_data_string
                )

            except json.JSONDecodeError:
                filtros = {}

        result = ReportsSales.search(
            user=user,
            page=filtros.get(
                'page',
                1
            ),
            key=filtros.get(
                'key'
            ),
            branch_id=filtros.get(
                'branch_id'
            ),
            user_id=filtros.get(
                'user_id'
            ),
            customer_id=filtros.get(
                'customer_id'
            ),
            status=filtros.get(
                'status'
            ),
            date_start=filtros.get(
                'date_start'
            ),
            date_end=filtros.get(
                'date_end'
            ),
            view_sales_totals=True
        )
        
        return JsonResponse(
            {
                "success":
                    result.get(
                        'success',
                        False
                    ),
                "message":
                    result.get(
                        'message',
                        ''
                    ),
                "answer":
                    result.get(
                        'answer',
                        []
                    ),
                "pagination":
                    result.get(
                        'pagination',
                        {}
                    ),
                "summary":
                    result.get(
                        'summary',
                        {}
                    ),
                "error":
                    result.get(
                        'error',
                        ''
                    )
            },
            status=200
        )

    except Exception as e:

        return JsonResponse(
            {
                "success": False,
                "message": "",
                "error": str(e)
            },
            status=500
        )


#======================================================VIEWS FOR REPORTS PDF AND EXCELS===========================================================
from apps.reports.services.excel.sales_report import generate_sales_excel_report, generate_sales_pdf_report
from apps.reports.services.excel.payments_report import generate_payment_methods_excel_report, generate_payment_methods_pdf_report
from apps.reports.services.excel.inevntory import generate_inventory_excel_report, generate_inventory_history_excel_report
def download_excel_sale(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200 
            )
    
    def get_param(name):
        val = request.GET.get(name)
        return val if val and val.strip() not in ['', 'undefined', 'null'] else None

    try:
        include_items=Plus.to_bool(get_param('include_items'))
        response = generate_sales_excel_report(
            company_id=request.user.company.id,
            start_date=get_param('start_date'),
            end_date=get_param('end_date'),
            user_id=get_param('user_id'),
            branch_id=get_param('branch_id'),
            customer_id=get_param('customer_id'),
            include_items=include_items,
            status=get_param('status'),
        )
        return response

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def download_pdf_sale(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_sales'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200 
            )
    
    def get_param(name):
        val = request.GET.get(name)
        return val if val and val.strip() not in ['', 'undefined', 'null'] else None

    try:
        include_items=Plus.to_bool(get_param('include_items'))
        response = generate_sales_pdf_report(
            company_id=request.user.company.id,
            start_date=get_param('start_date'),
            end_date=get_param('end_date'),
            user_id=get_param('user_id'),
            customer_id=get_param('customer_id'),
            include_items=include_items,
            status=get_param('status'),
            branch_id=get_param('branch_id')
        )
        return response

    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)

def download_excel_payment_methods(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_inventory'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    def get_param(name):
        val = request.GET.get(name)
        return val if val and val.strip() not in ['', 'undefined', 'null'] else None
    
    return generate_payment_methods_excel_report(
        company_id=request.user.company.id,
        start_date=get_param('start_date'),
        end_date=get_param('end_date'),
        user_id=get_param('user_id'),
        branch_id=get_param('branch_id'),
        method=get_param('method'),
        detailed=Plus.to_bool(get_param('details')),
    )

def download_pdf_payment_methods(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_inventory'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    def get_param(name):
        val = request.GET.get(name)
        return val if val and val.strip() not in ['', 'undefined', 'null'] else None
    
    return generate_payment_methods_pdf_report(
        company_id=request.user.company.id,
        start_date=get_param('start_date'),
        end_date=get_param('end_date'),
        user_id=get_param('user_id'),
        branch_id=get_param('branch_id'),
        method=get_param('method'),
        detailed=Plus.to_bool(get_param('details')),
    )

def get_report_inventory(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_move_money'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    return generate_inventory_excel_report(
        company_id=request.user.company.id,
        branch_id=request.user.branch.id
    )

def get_report_history_inventory(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_move_money'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    def get_param(name):
        val = request.GET.get(name)
        return val if val and val.strip() not in ['', 'undefined', 'null'] else None

    try:
        response = generate_inventory_history_excel_report(
            company_id=request.user.company.id,
            branch_id=get_param('branch_id'),

            start_date=get_param('start_date'),
            end_date=get_param('end_date'),
            user_id=get_param('user_id'),
            pack_id=get_param('pack_id'),
            unity_type=get_param('unity')
        )
        return response

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
def download_pdf_inventory(request):
    if not Plus.this_user_have_this_permission(request.user, 'watch_reports_move_money'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    def get_param(name):
        val = request.GET.get(name)
        return val if val and val.strip() not in ['', 'undefined', 'null'] else None

    try:
        response = generate_inventory_history_excel_report(
            company_id=request.user.company.id,
            branch_id=get_param('branch_id'),

            start_date=get_param('start_date'),
            end_date=get_param('end_date'),
            user_id=get_param('user_id'),
            pack_id=get_param('pack_id'),
            unity_type=get_param('unity')
        )
        return response

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)
    
