#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
@login_required(login_url='login')
def contract_home(request):
        return render(request, 'contract/home.html')

