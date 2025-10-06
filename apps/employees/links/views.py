from django.shortcuts import render
from django.http import JsonResponse
import json
from ..plus_wrapper import Plus

def employees_home(request):
    return render(request, 'home_employees.html')


from apps.employees.services.employees import get_employees_for_search
def search_employee(request, activated):
    if request.method == "POST":
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": "Method not allowed."
        }, status=405)  
    
    #now we will see if the user have the permsssion need that the ERP need
    if not Plus.this_user_have_this_permission(request.user, 'view_employee'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    


    try:
        search = request.GET.get("query")
        result = get_employees_for_search(
            company=request.user.company,
            branch=request.user.branch,
            sku=search,
            activated=activated
        )

        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

    except Exception as e:
        return JsonResponse({
            "success": False,
            "answer": [],
            "error": str(e)
        }, status=500) 