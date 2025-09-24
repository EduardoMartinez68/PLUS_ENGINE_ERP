from django.http import JsonResponse
from django.shortcuts import render
from apps.rolesAndPermissions.services.permits import get_all_the_permissions

def rolesAndPermissions_home(request):
    return render(request, 'home_rolesAndPermissions.html')


def get_all_the_permissions_of_the_erp(request):
    permissions = get_all_the_permissions()
    return JsonResponse({'success': True, 'answer': permissions}, status=200)
