from django.shortcuts import render
from django.http import JsonResponse
from ..plus_wrapper import Plus
import json


def medical_history_home(request):
    return render(request, 'home_medical_history.html')




#------------------------------
from ..services.medical import get_information_medical_in_list
def get_list_of_medical_history(request, page):
    if request.method == 'GET': 
        skull = request.GET.get("skull")
        result = get_information_medical_in_list(request.user, skull, page)

        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)