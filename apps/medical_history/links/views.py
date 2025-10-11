from django.shortcuts import render
from django.http import JsonResponse
from ..plus_wrapper import Plus
import json
from django.template.loader import render_to_string

def medical_history_home(request):
    return render(request, 'home_medical_history.html')




#------------------------------
from ..services.medical import get_information_medical_in_list, get_information_of_the_medical_history_for_customer_id
def get_list_of_medical_history(request, page):
    if request.method == 'GET': 
        skull = request.GET.get("skull")
        result = get_information_medical_in_list(request.user, skull, page)

        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

def view_history_medical(request, customer_id):
    result = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
    if result["success"]:
        html = render_to_string("view_medical_history.html", {"data": result["answer"]}, request=request)
        return JsonResponse({"success": True, "answer": html})
    else:
        return JsonResponse({"success": False, "error": result.get("error", "Unknown error")})

def get_medical_history_with_customer_id(request, customer_id):
    if request.method == 'GET': 
        result = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)

        return JsonResponse({"success": result["success"], "answer": result["answer"], 'error':result["error"]}, status=200) 
    

    return JsonResponse({"success": False, "answer": "Method not allowed"}, status=405)

def get_form_medical_history(request, customer_id):
    answer = get_information_of_the_medical_history_for_customer_id(request.user, customer_id)
    if answer["success"]:
        html = render_to_string("medical_history.html", {"patient": answer["answer"]}, request=request)
        return JsonResponse({"success": True, "answer": html})
    else:
        return JsonResponse({"success": False, "error": answer.get("error", "Unknown error")})
    
def form_history_medical(request, customer_id):
    result = {"customer_id": customer_id} 
    return render(request, 'form_medical_history.html', result) 