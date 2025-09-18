from django.shortcuts import render

def medical_history_home(request):
    return render(request, 'home_medical_history.html')
