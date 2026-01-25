from django.shortcuts import render
from django.http import JsonResponse
import json
from ..plus_wrapper import Plus

def employees_home(request):
    return render(request, 'employees/home_employees.html')


from ..services.employees import save_employee, get_information_of_employee_by_id, update_employee, change_employee_status
def add_employee(request):
    if request.method == "POST":
        #here we will to validate if the user have the subscription for that not can add more of that need
        sub = Plus.valid_subscription(request.user, 'employees')
        if not sub.get("status",False):
            return JsonResponse({"success": False,"message": sub.get("message"), "error": sub.get("error",'no can be this with the subscription that you have now')},status=200)
                
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'add_employee'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        result=save_employee(request.user.company,request.user.branch,data)

        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result['error']
        }, status=200) 
    







    
    return render(request, 'employees/add_employee.html')

from apps.employees.services.employees import get_employees_for_search
def search_employee(request, activated):
    if request.method == "POST":
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": "Method not allowed."
        }, status=405)  
    
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'view_employee_of_my_branch'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )


    all_filters = request.GET.get("allFilters", "")
    values = all_filters.split(",")
    search=values[0]
    branch_name = values[1].strip() if values[1] and values[1].strip() else request.user.branch
    some_flag = values[2] if values[2] not in (None, "") else True

    result = get_employees_for_search(
        company=request.user.company,
        branch= branch_name,
        sku=search,
        activated=some_flag
    )

    return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 



from apps.employees.services.branch import get_information_of_the_branch
def search_branch(request):
    if request.method == "POST":
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": "Method not allowed."
        }, status=405)  
    
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'view_employee_of_all_the_branch'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:
        search = request.GET.get("query")
        result = get_information_of_the_branch(
            company=request.user.company,
            name=search
        )

        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

    except Exception as e:
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": str(e)
        }, status=500) 
    







#-----------------------------
from django.template.loader import render_to_string
def edit_employee(request, employee_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        #now we will see if the user have the permsssion need that the ERP need
        if not Plus.this_user_have_this_permission(request.user, 'update_employee'):
            return JsonResponse(
                {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                status=200
            )
        
        result=update_employee(request.user.company, request.user.branch, employee_id, data)

        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result['error']
        }, status=200) 
    

    return render(request, 'employees/form.html', {'employee_id': employee_id})

def view_information_of_the_employee(request,id):
    employee=get_information_of_employee_by_id(request.user.company, id)
    html = render_to_string("employees/add_employee.html", {'employee': employee}, request=request)
    return JsonResponse({"success": True, "answer": html})
    '''
    
    answer = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
    if answer["success"]:
        html = render_to_string("medical_history.html", {"patient": answer["answer"]}, request=request)
        return JsonResponse({"success": True, "answer": html})
    else:
        return JsonResponse({"success": False, "error": answer.get("error", "Unknown error")})
    return render(request, 'add_employee.html')
    '''


def change_status(request, employee_id):
    if request.method == "GET":
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": "Method not allowed."
        }, status=405)  
    
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except Exception as e:
            return JsonResponse(
                {"success": False, "message": "Invalid JSON", "answer": "Invalid JSON", "error": str(e)}, 
                status=400
            )   
        
        #first we will see if the employee that the user would like change his status not is self
        if request.user.id==employee_id:
            return JsonResponse(
                {"success": False, "message": "message.error.not-can-change-the-status-of-your-self", "answer": 'message.error.not-can-change-the-status-of-your-self', "error": 'Not can change the status of your self'},
                status=200
            )         


        '''
        now we will see if the user have the permsssion need that the ERP need
        if the status is True is because the user need recover a employee and if the status
        is false is because the employee need delete to his companion
        '''
        status=data.get("status", False)
        if status:
            if not Plus.this_user_have_this_permission(request.user, 'recover_employee'):
                return JsonResponse(
                    {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                    status=200
                )
        else:
            if not Plus.this_user_have_this_permission(request.user, 'delete_employee'):
                return JsonResponse(
                    {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
                    status=200
                )
        

        result=change_employee_status(request.user.company, employee_id, status)
        return JsonResponse({
            "success": result['success'],
            "message": result['message'],
            "error": result['error']
        }, status=200) 
    
