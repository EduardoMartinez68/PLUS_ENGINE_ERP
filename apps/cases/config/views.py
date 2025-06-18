from django.shortcuts import render

def cases_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

def left_out(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

def case_home_2(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'index.html')
    else:
        return render(request, 'index.html')

