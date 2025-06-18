from django.shortcuts import render

def agenda_home(request):
    return render(request, 'agenda/index.html')