#PLUS Power by {ED} Software Developer
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from ..services.members import get_members_of_folder, delete_member_of_folder, add_member_to_folder, get_member_permissions_in_folder, update_member_permissions_in_folder
from django.http import FileResponse
from ..services.files import upload_file, get_folder_files, get_folders, get_folder_detail, create_folder, update_folder, delete_folder, download_file, get_file_detail, update_file, download_folder, delete_file, upload_multiple_files
from ..services.files import get_limit_of_the_user, user_storage_used_gb, format_size
from django.core.cache import cache
from ..models import File
from core.Plus import Plus
from django.http import Http404, JsonResponse, HttpResponse
import json
from django.shortcuts import render
@login_required(login_url='login')
def files_home(request):
        return render(request, 'files/home_files.html')

@login_required(login_url='login')
def get_settings_storge(request):
        if request.method == 'POST':
            user=request.user
    
            #try get the information of the cache of PLUS 
            cache_key = f"storage_used_{user.id}"
            answer = cache.get(cache_key)
    
            #if not exist in cache this information now we will get from the database
            if not answer:
                # 1. get the bytes that the user used (raw in Gb)
                gb_used = user_storage_used_gb(user)
                # 2. get the limit of the user in GB and convert it to bytes for can compare
                gb_limit = get_limit_of_the_user(user)
                
                # 3. Format for that the user can read "1.50 GB" or "500 KB"
                answer={'dataUsed': gb_used,  'dataMax': gb_limit}
    
                cache.set(cache_key, answer, 900) #save this information for 15 minutes 
    
            
            return JsonResponse({"success": True, "answer": answer, 'error':''}, status=200)  

@login_required(login_url='login')
def view_upload_file(request):
    
        if request.method != "POST":
    
            return JsonResponse({
                "success": False,
                "error": "invalid_method"
            })
    
        try:
    
            folder_id = request.POST.get(
                'folder_father_id'
            )
    
            uploaded_files = request.FILES.getlist(
                'files'
            )
    
            result = upload_multiple_files(
                user=request.user,
                folder_id=folder_id,
                request_data=request.POST,
                uploaded_files=uploaded_files
            )
    
            return JsonResponse(result)
    
        except Exception as e:
    
            return JsonResponse({
                "success": False,
                "error": str(e)
            })

@login_required(login_url='login')
def view_upload_file2(request):
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
def view_preview_file(request, file_id):
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
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_file_detail(request.user, file_id)
        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)

@login_required(login_url='login')
def view_download_file(request, file_id):
        if request.method != 'GET':
            raise Http404("Method not permitted")
    
        #get the file and the decrypt the file
        decrypted_content, file_instance = download_file(request.user, file_id)
        if not decrypted_content:
            raise Http404("File does not exist")
    
        #set the response to download the file
        response = HttpResponse(decrypted_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_instance.name}"'
        return response

@login_required(login_url='login')
def download_folder_as_zip(request, folder_id):
        import os 
        if request.method != 'GET':
            raise Http404("Method not permitted")
    
        result = download_folder(request.user, folder_id)
        if not result:
            raise Http404("Folder not found or permission denied")
    
        temp_zip, folder_name = result
        temp_zip.seek(0)
    
        # Abrimos el archivo temporal para el streaming
        zip_file = open(temp_zip.name, "rb")
    
        # Creamos la respuesta de descarga
        response = FileResponse(zip_file, as_attachment=True)
        response["Content-Disposition"] = f'attachment; filename="{folder_name}.zip"'
    
        # 🔹 Limpieza automática al terminar de enviar el archivo
        def cleanup_file(file_path):
            try:
                zip_file.close()
                os.remove(file_path)
            except Exception:
                pass
    
        # Django llama a 'close' cuando termina la transmisión
        response.close = lambda *args, **kwargs: (
            cleanup_file(temp_zip.name),
            super(FileResponse, response).close(*args, **kwargs)
        )
    
        return response

@login_required(login_url='login')
def view_update_file(request, file_id):
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=update_file(request.user, file_id, data)
        return JsonResponse({"success": result["success"], 'error':result["error"]}, status=200)

@login_required(login_url='login')
def view_delete_file(request):
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=delete_file(request.user, data["id"])
        return JsonResponse({"success": result["success"], "message": result["message"], "answer": result["answer"], 'error':result["error"]}, status=200)   

@login_required(login_url='login')
def get_information_folder(request, folder_id):
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result = get_folder_detail(request.user, folder_id)
        return JsonResponse({"success": result["success"], "message": result["message"], "answer": result["answer"], 'error':result["error"]}, status=200)  

@login_required(login_url='login')
def create_new_folder(request):
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
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=delete_folder(request.user, data["id"])
        return JsonResponse({"success": result["success"], "message": result["message"], "answer": result["answer"], 'error':result["error"]}, status=200)  

@login_required(login_url='login')
def members_of_folder(request):
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        #get the filters of the folder
        all_filters = request.GET.get("allFilters", "") 
        values = all_filters.split(",")
        search=values[0] #query
        folder_id=values[1] #id folder
        result = get_members_of_folder(request.user, folder_id, search)
        return JsonResponse({"success": result.get("success", False), "message": result.get("message", ''), "answer": result.get("answer", []), 'error': result.get("error", "")}, status=200)

@login_required(login_url='login')
def view_delete_member_folder(request, folder_id):
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        member_id=data.get("id")
    
        result=delete_member_of_folder(request.user, folder_id, member_id)
        return JsonResponse({"success": result["success"], "message": result["message"], 'error':result["error"]}, status=200)

@login_required(login_url='login')
def view_add_member_folder(request):
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
    
        member_id=data.get("member_id")
        folder_id=data.get("folder_id")
    
        result=add_member_to_folder(request.user, folder_id, member_id, data)
        return JsonResponse({"success": result["success"], "message": result["message"], 'error':result["error"]}, status=200)

@login_required(login_url='login')
def get_permitions_member(request, folder_id, member_id):
        if request.method != 'GET':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        result=get_member_permissions_in_folder(request.user, folder_id, member_id)
    
        return JsonResponse({"success": result["success"], "message": result["message"], "answer": result["answer"], 'error':result["error"]}, status=200)

@login_required(login_url='login')
def view_update_member_in_the_folder(request):
        if request.method != 'POST':
            return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
        
        result=update_member_permissions_in_folder(request.user, data.get("folder_id", "") ,data.get("member_id", "") , data) 
        return JsonResponse({"success": result["success"], "message": result["message"], "answer": result["answer"], 'error':result["error"]}, status=200)

