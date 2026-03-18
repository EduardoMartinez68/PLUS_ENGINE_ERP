#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from apps.dashboard.services.dashboard import get_information_dashboard
from django.shortcuts import render
from django.http import JsonResponse
@login_required(login_url='login')
def dashboard_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'dashboard/home_dashboard.html')
    else:
        return render(request, 'dashboard/home_dashboard.html')

@login_required(login_url='login')
def view_get_information_dashboard(request, slug):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        answer=get_information_dashboard(request, slug)
        return JsonResponse({'success': True, 'answer': answer}, status=200)
    else:
        answer=get_information_dashboard(request, slug)
        return JsonResponse({'success': True, 'answer': answer}, status=200)

