from django.shortcuts import render
from django.http import JsonResponse

def files_home(request):
    return render(request, 'home_files.html')


def upload_file(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        name = request.POST.get('name')
        description = request.POST.get('description')
        anchored = request.POST.get('anchored') == 'on'

        print(name)
        print(file)

        return JsonResponse({'success': True, 'message': 'Archivo subido correctamente'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)