#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from django.shortcuts import render
@login_required(login_url='login')
def agenda_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_agenda.html')
    else:
        return render(request, 'home_agenda.html')

@login_required(login_url='login')
def create_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            #get the information of the form
            data = json.loads(request.body)
            title = data.get('title', '')
            color = data.get('color', '')
    
            #now we will see if exists the name
            if(title==''):
                return JsonResponse({'success': False, 'message': 'Se necesita un nombre para el tipo de evento.'}, status=400)
    
            print(request.user)
            return JsonResponse({'success': True, 'message': 'Cliente editado exitosamente.'})
        else:
            return JsonResponse({'success': False, 'message': 'Error al editar el cliente.', 'error': str(e)}, status=500)
    else:
        if request.method == 'POST':
            #get the information of the form
            data = json.loads(request.body)
            title = data.get('title', '')
            color = data.get('color', '')
    
            #now we will see if exists the name
            if(title==''):
                return JsonResponse({'success': False, 'message': 'Se necesita un nombre para el tipo de evento.'}, status=400)
    
            print(request.user)
            return JsonResponse({'success': True, 'message': 'Cliente editado exitosamente.'})
        else:
            return JsonResponse({'success': False, 'message': 'Error al editar el cliente.', 'error': str(e)}, status=500)

