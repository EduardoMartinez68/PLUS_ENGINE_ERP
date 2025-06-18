from django.shortcuts import render

def cases_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # llamada AJAX (SPA)
        return render(request, 'index.html')
    else:
        # navegación normal
        return render(request, 'index.html')