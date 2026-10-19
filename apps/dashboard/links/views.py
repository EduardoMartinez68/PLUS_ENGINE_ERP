from django.http import JsonResponse
from django.shortcuts import render

def dashboard_home(request):
    return render(request, 'dashboard/home_dashboard.html')


from apps.dashboard.services.dashboard import get_information_dashboard
def view_get_information_dashboard(request, slug):
    answer=get_information_dashboard(request, slug)
    return JsonResponse({'success': True, 'answer': answer}, status=200)

from core.Plus import Plus
from apps.dashboard.services.dashboard import Dashboard
def dashboard_data(request):
    if request.method != "GET":
        return JsonResponse({"success": False}, status=405)

    #if not Plus.this_user_have_this_permission(request.user, 'view_dashboard'):
        #return JsonResponse({
            #"success": False,
            #"error": "no permission"
        #})

    result = Dashboard.get_dashboard_data(request.user)
    return JsonResponse(result, status=200)