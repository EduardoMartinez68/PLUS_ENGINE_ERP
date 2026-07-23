#==========================EXAMPLES SAVE SERVICES==========================
from core.plus.ServiceRegistry import ServiceRegistry
from apps.customers.services.Customers import Customers

ServiceRegistry["customers.add_customer"] = Customers.add_new_customer


#in the views we run the plugins and the logic service of this form 
from core.plus.PluginManager import PluginManager
import json
from django.http import JsonResponse
from core.Plus import Plus

def do_a_sale(request, sale_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)
    
    if not Plus.this_user_have_this_permission(request.user, 'add_sales'):
        return JsonResponse(
            {"success": False, "answer": 'message.this-user-not-have-this-permission', "error": 'this user not have this permission'},
            status=200
        )
    
    try:
        data = json.loads(request.body)
        result = PluginManager.execute(
            "Sales.do_a_sale",
            user=request.user,
            sale_id=sale_id,
            data=data
        )
        return JsonResponse({
            "success": result.get('success', False),
            "message": result.get('message', ''),
            "answer": result.get('answer', []),
            "error": result.get('error', ''),
            "data": result.get('data', {})
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "message": "message.invalid-json",
            "error": "Invalid JSON"
        }, status=400)

#==========================EXAMPLES OF PLUGINS==========================
from plus import hooks
@hooks.after("customers.add_customer")
def save_log(ctx):

    Log.create(
        user=ctx.user,
        customer=ctx.result.id
    )

@hooks.before("customers.add_customer")
def validate(ctx):

    if ctx.data["age"] < 18:
        raise Exception("No permitido")