#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..models import Customer
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
@login_required(login_url='login')
def customers_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        id_company = request.user.id_company
    
        # get the first 20 answers from the branch ordered by ID and that his status is True
        customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
    
        return render(request, 'customers.html', {'customers': customers})
    else:
        id_company = request.user.id_company
    
        # get the first 20 answers from the branch ordered by ID and that his status is True
        customers = Customer.objects.filter(id_company=id_company.id, activated=True).order_by('id')[:20]
    
        return render(request, 'customers.html', {'customers': customers})

@login_required(login_url='login')
def search_customers_select(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            result_list = []
    
            result_list.append({
                'id': 1,
                'text': 'pablo'
            })
            return JsonResponse({'success': True,'results': result_list})
        else:
            return JsonResponse({'message': 'Método no permitido'}, status=405)
    else:
        if request.method == 'POST':
            result_list = []
    
            result_list.append({
                'id': 1,
                'text': 'pablo'
            })
            return JsonResponse({'success': True,'results': result_list})
        else:
            return JsonResponse({'message': 'Método no permitido'}, status=405)

