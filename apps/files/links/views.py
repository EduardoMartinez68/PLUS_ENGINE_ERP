from django.shortcuts import render
from django.http import JsonResponse
from ..plus_wrapper import Plus

def files_home(request):
    return render(request, 'home_files.html')



from ..services.files import upload_file, get_folder_files
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


def view_files_of_the_folder(request, folder_id):
    if request.method == 'GET':
        result=get_folder_files(folder_id) 