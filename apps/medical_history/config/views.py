#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required(login_url='login')
def medical_history_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_medical_history.html')
    else:
        return render(request, 'home_medical_history.html')

