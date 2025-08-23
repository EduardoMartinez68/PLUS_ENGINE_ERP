#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
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

