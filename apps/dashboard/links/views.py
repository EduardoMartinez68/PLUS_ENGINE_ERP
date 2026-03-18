from django.http import JsonResponse
from django.shortcuts import render

def dashboard_home(request):
    return render(request, 'dashboard/home_dashboard.html')


from apps.dashboard.services.dashboard import get_information_dashboard
def view_get_information_dashboard(request, slug):
    answer=get_information_dashboard(request, slug)
    return JsonResponse({'success': True, 'answer': answer}, status=200)