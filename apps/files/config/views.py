#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.files import upload_file, get_folder_files, get_root_folders
from ..plus_wrapper import Plus
from django.http import JsonResponse
from django.shortcuts import render
@login_required(login_url='login')
def files_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_files.html')
    else:
        return render(request, 'home_files.html')

@login_required(login_url='login')
def upload_file(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            file = request.FILES.get('file')
            name = request.POST.get('name')
            description = request.POST.get('description')
            anchored = Plus.to_bool(request.POST.get('anchored'))
            folder_id = request.POST.get('folder')
    
            #here we will see if exist a file
            if not file:
                return JsonResponse({'success': False, 'message': 'files.message.not-exist-file'}, status=400)
    
            # struct of the data
            dataFile = {
                "file": file,
                "name": name,
                "description": description,
                "anchored": anchored,
                "folder": folder_id,
            }
    
      
            result = upload_file(request.user, dataFile)
    
            return JsonResponse(result, status=200 if result["success"] else 400)
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    else:
        if request.method == 'POST':
            file = request.FILES.get('file')
            name = request.POST.get('name')
            description = request.POST.get('description')
            anchored = Plus.to_bool(request.POST.get('anchored'))
            folder_id = request.POST.get('folder')
    
            #here we will see if exist a file
            if not file:
                return JsonResponse({'success': False, 'message': 'files.message.not-exist-file'}, status=400)
    
            # struct of the data
            dataFile = {
                "file": file,
                "name": name,
                "description": description,
                "anchored": anchored,
                "folder": folder_id,
            }
    
      
            result = upload_file(request.user, dataFile)
    
            return JsonResponse(result, status=200 if result["success"] else 400)
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

@login_required(login_url='login')
def view_files_of_the_folder(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)
    
        user = request.user
        result = get_root_folders(user, user.company, user.branch)
        print(result)
    
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    else:
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Método no permitido"}, status=405)
    
        user = request.user
        result = get_root_folders(user, user.company, user.branch)
        print(result)
    
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

