from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import Contracts
from django.contrib import messages
from datetime import datetime
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def contracts_home(request):
    user_id = request.user.id
    # get the first 20 contarcts of the user
    # we will order by creation_date desc
    contracts = Contracts.objects.filter(user_id=user_id).order_by('-creation_date')[:20]
    
    context = {
        'contracts': contracts
    }
    return render(request, 'home_contracts.html', context)



@csrf_exempt
def add_contract(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # El body lo mandas en JSON con fetch

            # Extraer los datos del JSON
            name = data.get('name', '').strip()

            #we will see if the user add the name of the contract
            if not name:
                return JsonResponse({'success': False, 'message': 'El nombre del contrato es obligatorio.','error': ''}, status=400)

            #now we will save the contract
            user_id= request.user.id
            id_branch = request.user.id_branch
            container_editor = data.get('container_editor', '').strip()
            creation_date = datetime.now()

            #her we will add the new contract to the database

            contract = Contracts(
                user_id = user_id,
                title=name,
                content_html=container_editor,
                active=True,
                creation_date=creation_date
            )
            contract.save()

            return JsonResponse({'success': True, 'message': 'Contrato agregado exitosamente.'})

        except Exception as e:
            print('--------------------- ERROR to save the add_contract---------------------')
            print(e)
            return JsonResponse({'success': False, 'message':'El contrato no pudo guardarse.','error': f'Error al crear el contrato: {e}'}, status=500)



    return render(request, 'add_contracts.html')


@csrf_exempt
def edit_contract(request, contract_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # El body viene en JSON con fetch

            # Extraer datos del JSON
            name = data.get('name', '').strip()
            container_editor = data.get('container_editor', '').strip()

            # Verificar que haya nombre
            if not name:
                return JsonResponse({'success': False, 'message': 'El nombre del contrato es obligatorio.', 'error': ''}, status=400)

            # Buscar el contrato existente
            try:
                contract = Contracts.objects.get(id=contract_id, user_id=request.user.id)
            except Contracts.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Contrato no encontrado.', 'error': ''}, status=404)

            # Actualizar los campos
            contract.title = name
            contract.content_html = container_editor
            contract.save()

            return JsonResponse({'success': True, 'message': 'Contrato editado exitosamente.'})

        except Exception as e:
            print('--------------------- ERROR edit_contract ---------------------')
            print(e)
            return JsonResponse({'success': False, 'message': 'Error al editar el contrato.', 'error': str(e)}, status=500)

    # Si es GET, mostrar el formulario de edición
    try:
        contract = Contracts.objects.get(id=contract_id, user_id=request.user.id)
    except Contracts.DoesNotExist:
        return HttpResponse("Contrato no encontrado.", status=404)

    return render(request, 'edit_contracts.html', {'contract': contract})
