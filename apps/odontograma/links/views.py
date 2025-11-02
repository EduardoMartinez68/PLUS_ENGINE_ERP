from django.shortcuts import render
from ..plus_wrapper import Plus
from django.http import JsonResponse

def odontograma_home(request):
    return render(request, 'home_odontograma.html')



from ..services.odontogram import get_odontograms
def search_odontogram(request):
    if request.method != 'GET': 
        return JsonResponse({"success": False, "message": "Method not permitted"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'view_odontogram'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        ) 


    search = request.GET.get("query", "") 
    result=get_odontograms(request.user, search) 
    return JsonResponse({"success": result.get("success", False), "message": result.get("message", 'not exist message'), "answer": result.get("answer", []), 'error':result.get("error", 'not exist error in the return')}, status=200)



def add_odontogram(request):
    return render(request, 'load_form_odontograma.html')

def get_odontogram(request, odontogram_id):
    return render(request, 'home_odontograma.html')