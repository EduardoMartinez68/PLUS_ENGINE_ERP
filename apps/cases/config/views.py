#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
@login_required(login_url='login')
def cases_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

@login_required(login_url='login')
def left_out(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

@login_required(login_url='login')
def case_home_2(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

