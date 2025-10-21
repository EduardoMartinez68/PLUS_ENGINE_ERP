#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.files import upload_file, get_folder_files, get_folders, get_folder_detail, create_folder, update_folder, delete_folder
from ..models import Folder, FolderPermission
from ..plus_wrapper import Plus
from django.http import JsonResponse
import json
from django.shortcuts import render
@login_required(login_url='login')
def files_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_files.html')
    else:
        return render(request, 'home_files.html')

@login_required(login_url='login')
def upload_file(request, folder_id):
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
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        
        #get the filters of the folder
        all_filters = request.GET.get("allFilters", "") 
        values = all_filters.split(",")
        search=values[0] #query
        folder_id=values[1] #id folder
        
        user = request.user
        result = get_folder_files(user, folder_id, search)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    else:
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        
        #get the filters of the folder
        all_filters = request.GET.get("allFilters", "") 
        values = all_filters.split(",")
        search=values[0] #query
        folder_id=values[1] #id folder
        
        user = request.user
        result = get_folder_files(user, folder_id, search)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

@login_required(login_url='login')
def view_folders_of_the_folder(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        
        #get the filters of the folder
        all_filters = request.GET.get("allFilters", "") 
        values = all_filters.split(",")
        search=values[0] #query
        folder_id=values[1] #id folder
    
        user = request.user
        result = get_folders(user, folder_id, search)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  
    else:
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        
        #get the filters of the folder
        all_filters = request.GET.get("allFilters", "") 
        values = all_filters.split(",")
        search=values[0] #query
        folder_id=values[1] #id folder
    
        user = request.user
        result = get_folders(user, folder_id, search)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  

@login_required(login_url='login')
def get_information_folder(request, folder_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_folder_detail(request.user, folder_id)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  
    else:
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_folder_detail(request.user, folder_id)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  

@login_required(login_url='login')
def create_new_folder(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=create_folder(request.user, data['folder_father_id'], data)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  
    else:
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=create_folder(request.user, data['folder_father_id'], data)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  

@login_required(login_url='login')
def edit_folder(request, folder_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=update_folder(request.user, folder_id, data)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  
    else:
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=update_folder(request.user, folder_id, data)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  

@login_required(login_url='login')
def delete_folder_and_his_files(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=delete_folder(request.user, data["id"])
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  
    else:
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=delete_folder(request.user, data["id"])
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  

