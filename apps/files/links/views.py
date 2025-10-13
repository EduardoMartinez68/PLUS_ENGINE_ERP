from django.shortcuts import render

def files_home(request):
    return render(request, 'home_files.html')
