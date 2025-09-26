from django.http import JsonResponse
from django.shortcuts import render
import json
from apps.rolesAndPermissions.services.permits import get_all_the_permissions
from apps.rolesAndPermissions.services.role import get_role_of_the_company

def rolesAndPermissions_home(request):
    return render(request, 'home_rolesAndPermissions.html')

def get_information_of_the_role(request):
    if request.method == "GET": 
        name = request.GET.get("query", "")
        page = request.GET.get("page", 1)

        company = getattr(request.user, "company", None)

        answer = get_role_of_the_company(company, name=name, page=page)
        return JsonResponse(answer, status=200)

    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)




def get_all_the_permissions_of_the_erp(request):
    if request.method == "GET": 
        '''
        get all the permissions that exist in this ERP. Not need a company id or a user id because
        the permissions be load from the apps of the ERP not from a company or a user
        '''
        permissions = get_all_the_permissions()
        return JsonResponse({'success': True, 'answer': permissions}, status=200)




from apps.rolesAndPermissions.services.role import save_a_new_role
def add_a_new_rol(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        #save_a_new_role(request.user, data)


        return JsonResponse({'success': True, 'answer': ''}, status=200)
    elif request.method == "GET":
        return render(request, 'form_rol.html')