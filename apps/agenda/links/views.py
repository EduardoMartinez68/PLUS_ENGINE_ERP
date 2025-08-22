from django.shortcuts import render
import json
from django.http import JsonResponse

def agenda_home(request):
    return render(request, 'home_agenda.html')


def create_type_event(request):
    if request.method == 'POST':
        #get the information of the form
        data = json.loads(request.body)
        title = data.get('title', '')
        color = data.get('color', '')

        #now we will see if exists the name
        if(title==''):
            return JsonResponse({'success': False, 'message': 'message.need_a_name_for_the_type_event', 'error': 'Need the title of the type event'}, status=400)

        print(request.user)
        return JsonResponse({'success': True, 'message': 'Cliente editado exitosamente.'})
    else:
        return JsonResponse({'success': False, 'message': 'Error al editar el cliente.', 'error': str(e)}, status=500)
