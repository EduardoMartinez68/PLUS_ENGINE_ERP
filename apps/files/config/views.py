#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from ..services.files import upload_file, get_folder_files, get_folders, get_folder_detail, create_folder, update_folder, delete_folder, download_file, get_file_detail, update_file
from ..models import Folder, FolderPermission, File
from ..plus_wrapper import Plus
from django.http import Http404, JsonResponse, HttpResponse
import json
from django.shortcuts import render
@login_required(login_url='login')
def files_home(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'home_files.html')
    else:
        return render(request, 'home_files.html')

@login_required(login_url='login')
def view_upload_file(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method == 'POST':
            folder_father_id = request.POST.get('folder_father_id')
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
    
      
            result = upload_file(request.user, folder_father_id, dataFile)
    
            return JsonResponse(result, status=200 if result["success"] else 400)
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)
    else:
        if request.method == 'POST':
            folder_father_id = request.POST.get('folder_father_id')
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
    
      
            result = upload_file(request.user, folder_father_id, dataFile)
    
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
        files=[]
        
        if result["success"]:
            files = result["answer"]["files"] 
    
        return JsonResponse({"success": result["success"], "answer": files, 'error':result["error"]}, status=200) 
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
        files=[]
        
        if result["success"]:
            files = result["answer"]["files"] 
    
        return JsonResponse({"success": result["success"], "answer": files, 'error':result["error"]}, status=200) 

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
def view_download_file(request, file_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            raise Http404("File does not exist")
    
        #get the file and the decrypt the file
        decrypted_content, file_instance = download_file(request.user, file_id)
        if not decrypted_content:
            raise Http404("File does not exist")
    
        #set the response to download the file
        response = HttpResponse(decrypted_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_instance.name}"'
        return response
    else:
        if request.method != 'GET':
            raise Http404("File does not exist")
    
        #get the file and the decrypt the file
        decrypted_content, file_instance = download_file(request.user, file_id)
        if not decrypted_content:
            raise Http404("File does not exist")
    
        #set the response to download the file
        response = HttpResponse(decrypted_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_instance.name}"'
        return response

@login_required(login_url='login')
def view_preview_file(request, file_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            raise Http404("File does not exist")
    
        # get the file and decrypt the file
        decrypted_content = download_file(request.user, file_id)
        if not decrypted_content:
            raise Http404("File does not exist")
    
        # get the instance for know that type of files be 
        try:
            file_instance = File.objects.get(id=file_id)
        except File.DoesNotExist:
            raise Http404("File does not exist")
    
        # determine type MIME with help of his extension
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_instance.name)
        if not mime_type:
            mime_type = "application/octet-stream"
    
        response = HttpResponse(decrypted_content, content_type=mime_type)
    
        return response
    else:
        if request.method != 'GET':
            raise Http404("File does not exist")
    
        # get the file and decrypt the file
        decrypted_content = download_file(request.user, file_id)
        if not decrypted_content:
            raise Http404("File does not exist")
    
        # get the instance for know that type of files be 
        try:
            file_instance = File.objects.get(id=file_id)
        except File.DoesNotExist:
            raise Http404("File does not exist")
    
        # determine type MIME with help of his extension
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_instance.name)
        if not mime_type:
            mime_type = "application/octet-stream"
    
        response = HttpResponse(decrypted_content, content_type=mime_type)
    
        return response

@login_required(login_url='login')
def get_information_file(request, file_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_file_detail(request.user, file_id)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)
    else:
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_file_detail(request.user, file_id)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)

@login_required(login_url='login')
def view_update_file(request, file_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=update_file(request.user, file_id, data)
        return JsonResponse({"success": result["success"], 'error':result["error"]}, status=200)
    else:
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=update_file(request.user, file_id, data)
        return JsonResponse({"success": result["success"], 'error':result["error"]}, status=200)

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

