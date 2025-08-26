#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..models import TypeAppoint
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
def get_the_first_type_events(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            # Logic to retrieve the first events
            events = []  # Replace with actual event retrieval logic
            return JsonResponse({'success': True, 'results': events})
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)
    else:
        if request.method == 'POST':
            # Logic to retrieve the first events
            events = []  # Replace with actual event retrieval logic
            return JsonResponse({'success': True, 'results': events})
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

@login_required(login_url='login')
def create_type_event(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD')
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)
    
                # create and save the new TypeAppoint
                new_type = TypeAppoint(
                    name=title,
                    color=color,
                    user=request.user
                )
                new_type.save()
                
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento creado exitosamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al crear el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)
    else:
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                title = data.get('title', '').strip()
                color = data.get('color', '#075EAD')
    
                if title == '':
                    return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)
    
                # create and save the new TypeAppoint
                new_type = TypeAppoint(
                    name=title,
                    color=color,
                    user=request.user
                )
                new_type.save()
                
    
                return JsonResponse({'success': True, 'message': 'Tipo de evento creado exitosamente.'})
            
            except Exception as e:
                return JsonResponse({'success': False, 'message': 'Error al crear el tipo de evento.', 'error': str(e)}, status=500)
    
        return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

