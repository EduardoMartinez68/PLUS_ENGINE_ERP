#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from io import BytesIO
from django.shortcuts import get_object_or_404
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.http import HttpResponse
import re
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from .models import Contracts
from django.shortcuts import render, redirect
from django.shortcuts import render
@login_required(login_url='login')
def contracts_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user_id = request.user.id
        # get the first 20 contarcts of the user
        # we will order by creation_date desc
        contracts = Contracts.objects.filter(user_id=user_id).order_by('-creation_date')[:20]
        
        context = {
            'contracts': contracts
        }
        return render(request, 'home_contracts.html', context)
    else:
        user_id = request.user.id
        # get the first 20 contarcts of the user
        # we will order by creation_date desc
        contracts = Contracts.objects.filter(user_id=user_id).order_by('-creation_date')[:20]
        
        context = {
            'contracts': contracts
        }
        return render(request, 'home_contracts.html', context)

@login_required(login_url='login')
def add_contract(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
                creation_date = timezone.now()
    
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
    else:
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
                creation_date = timezone.now()
    
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

@login_required(login_url='login')
def edit_contract(request, contract_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
                return JsonResponse({'success': False, 'message': 'Error al editar el contrato.', 'error': e}, status=500)
    
        # Si es GET, mostrar el formulario de edición
        try:
            contract = Contracts.objects.get(id=contract_id, user_id=request.user.id)
        except Contracts.DoesNotExist:
            return HttpResponse("Contrato no encontrado.", status=404)
    
        return render(request, 'edit_contracts.html', {'contract': contract})
    else:
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
                return JsonResponse({'success': False, 'message': 'Error al editar el contrato.', 'error': e}, status=500)
    
        # Si es GET, mostrar el formulario de edición
        try:
            contract = Contracts.objects.get(id=contract_id, user_id=request.user.id)
        except Contracts.DoesNotExist:
            return HttpResponse("Contrato no encontrado.", status=404)
    
        return render(request, 'edit_contracts.html', {'contract': contract})

@login_required(login_url='login')
def detect_type_input(request, label):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if "date" in label or "Fecha.Actual" in label or "Fecha" in label:
            return "date"
        elif "Monto" in label or "Total" in label:
            return "Number"
        else:
            return "text"
    else:
        if "date" in label or "Fecha.Actual" in label or "Fecha" in label:
            return "date"
        elif "Monto" in label or "Total" in label:
            return "Number"
        else:
            return "text"

@login_required(login_url='login')
def form_contract(request, contract_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
    
        #get the information of the file
        contract = get_object_or_404(Contracts, id=contract_id, user_id=request.user.id)
    
        #her we will get all the labels of the document for after create the form
        text_html=contract.content_html
        labels=re.findall(r'\{\{(.*?)\}\}',text_html)
    
    
        if request.method == 'POST':
            data=json.loads(request.body)
            for label in labels: 
                value=data.get(label,'')
                
                text_html=text_html.replace(f'{{{{{label}}}}}',value)
    
            #we will create a object BytesIO for save the PDF in memory
            result = BytesIO()
    
            # convert the HTML to PDF use pisa (her we use the value remplace in the text_html)
            pdf = pisa.pisaDocument(BytesIO(text_html.encode('UTF-8')), dest=result)
    
            # Check if there was an error during PDF generation
            if pdf.err:
                return HttpResponse('Error al generar el PDF', status=500)
    
            #return the PDF as a response
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{contract.title}.pdf"'
            return response
        
        #if not is a for post, we will show the inputs of the file
        #now we create a list of inputs for the form
        inputs=[]
        labels_seen = set() #this is to avoid duplicate labels
        for label in labels:
            if label not in labels_seen:
                labels_seen.add(label)
                input={
                    "name":label,
                    "label":label.replace('.',' '),
                    "type":detect_type_input(request,label),
                    "value":""
                }
    
                inputs.append(input)
    
        return render(request, 'form_contracts.html', {'contract': contract,'inputs':inputs})
    else:
    
        #get the information of the file
        contract = get_object_or_404(Contracts, id=contract_id, user_id=request.user.id)
    
        #her we will get all the labels of the document for after create the form
        text_html=contract.content_html
        labels=re.findall(r'\{\{(.*?)\}\}',text_html)
    
    
        if request.method == 'POST':
            data=json.loads(request.body)
            for label in labels: 
                value=data.get(label,'')
                
                text_html=text_html.replace(f'{{{{{label}}}}}',value)
    
            #we will create a object BytesIO for save the PDF in memory
            result = BytesIO()
    
            # convert the HTML to PDF use pisa (her we use the value remplace in the text_html)
            pdf = pisa.pisaDocument(BytesIO(text_html.encode('UTF-8')), dest=result)
    
            # Check if there was an error during PDF generation
            if pdf.err:
                return HttpResponse('Error al generar el PDF', status=500)
    
            #return the PDF as a response
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{contract.title}.pdf"'
            return response
        
        #if not is a for post, we will show the inputs of the file
        #now we create a list of inputs for the form
        inputs=[]
        labels_seen = set() #this is to avoid duplicate labels
        for label in labels:
            if label not in labels_seen:
                labels_seen.add(label)
                input={
                    "name":label,
                    "label":label.replace('.',' '),
                    "type":detect_type_input(request,label),
                    "value":""
                }
    
                inputs.append(input)
    
        return render(request, 'form_contracts.html', {'contract': contract,'inputs':inputs})

@login_required(login_url='login')
def download_contract(request, contract_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        contract = get_object_or_404(Contracts, id=contract_id, user_id=request.user.id)
    
        # Renderiza el HTML con la plantilla y el contrato
        html_string = render_to_string('pdf_template.html', {'contract': contract})
    
        # Crear un objeto BytesIO para guardar el PDF en memoria
        result = BytesIO()
    
        # Convertir HTML a PDF usando pisa
        pdf = pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), dest=result)
    
        if pdf.err:
            return HttpResponse('Error al generar el PDF', status=500)
    
        # Retornar el PDF generado
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Contrato_{contract.id}.pdf"'
        return response
    else:
        contract = get_object_or_404(Contracts, id=contract_id, user_id=request.user.id)
    
        # Renderiza el HTML con la plantilla y el contrato
        html_string = render_to_string('pdf_template.html', {'contract': contract})
    
        # Crear un objeto BytesIO para guardar el PDF en memoria
        result = BytesIO()
    
        # Convertir HTML a PDF usando pisa
        pdf = pisa.pisaDocument(BytesIO(html_string.encode('UTF-8')), dest=result)
    
        if pdf.err:
            return HttpResponse('Error al generar el PDF', status=500)
    
        # Retornar el PDF generado
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Contrato_{contract.id}.pdf"'
        return response

