from django.shortcuts import render
import json
from django.http import JsonResponse
from ..plus_wrapper import Plus
from ..models import Folder, FolderPermission

def files_home(request):
    return render(request, 'home_files.html')



from ..services.files import upload_file, get_folder_files, get_root_folders, get_folder_detail, create_folder
def upload_file(request):
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

def view_files_of_the_folder(request):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)

    user = request.user
    result = get_root_folders(user, user.company, user.branch)
    print(result)
    return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 

def get_information_folder(request, folder_id):
    if request.method != 'GET':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    result = get_folder_detail(request.user, folder_id)
    return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  

def create_new_folder(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message":"" , "error": "Format JSON invalid"}, status=400)
    
    result=create_folder(request.user, None, data)
    return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200)  