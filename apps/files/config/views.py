#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
@login_required(login_url='login')
def files_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_files.html')
    else:
        return render(request, 'home_files.html')

@login_required(login_url='login')
def upload_file(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            file = request.FILES.get('file')
            name = request.POST.get('name')
            description = request.POST.get('description')
            anchored = request.POST.get('anchored') == 'on'
    
            print(name)
            print(file)
    
            return JsonResponse({'success': True, 'message': 'Archivo subido correctamente'})
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    else:
        if request.method == 'POST':
            file = request.FILES.get('file')
            name = request.POST.get('name')
            description = request.POST.get('description')
            anchored = request.POST.get('anchored') == 'on'
    
            print(name)
            print(file)
    
            return JsonResponse({'success': True, 'message': 'Archivo subido correctamente'})
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

