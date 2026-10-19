#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from apps.dashboard.services.dashboard import Dashboard
from core.Plus import Plus
from apps.dashboard.services.dashboard import get_information_dashboard
from django.shortcuts import render
from django.http import JsonResponse
@login_required(login_url='login')
def dashboard_home(request):
        return render(request, 'dashboard/home_dashboard.html')

@login_required(login_url='login')
def view_get_information_dashboard(request, slug):
        answer=get_information_dashboard(request, slug)
        return JsonResponse({'success': True, 'answer': answer}, status=200)

@login_required(login_url='login')
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

