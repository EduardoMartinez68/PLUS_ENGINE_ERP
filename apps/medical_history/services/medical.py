from ..models import MedicalInformation
from typing import Dict, Any, List

'''
this function is for get the information that we will show in the screen of the frontend of the home. 
Need the user that is be the application from the frontend, the skull and the page that need.
'''
def get_information_medical_in_list(user, skull: str='', page:int=1, limit:int=20)->Dict[str, Any]:
    company = getattr(user, "company", None)
    if not company:
        return {
            "success": False,
            "answer": "medical-history.message.server.error.no-exist-the-company",
            "error": "Company is required"
        }

    try:
        queryset = MedicalInformation.objects.filter(company=company).select_related("customer")

        # filter for skull if exist
        if skull:
            queryset = queryset.filter(skull__icontains=skull)

        queryset = queryset.order_by("-created_at")

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        results = queryset[start:end]


        #get the information that show in the screen of the frontend
        data = []
        for item in results:
            customer = item.customer
            data.append({
                "id": item.id,
                "skull": item.skull,
                "blood_type": item.blood_type,
                "created_at": item.created_at,
                "updated_at": item.updated_at,

                # ---- information of the customer ----
                "customer_id": customer.id,
                "avatar": customer.avatar.url if customer.avatar else None,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "cellphone": customer.cellphone,
            })



        return {
            "success": True,
            "answer": data,
            "error": 'Information get with success',
            #this information is for update the frontend 
            "pagination": {
                "page": page,
                "limit": limit,
                "total": queryset.count()
            }
        }

    except Exception as e:
        return {
            "success": False,
            "answer": "medical-history.message.server.error.error-in-the-server",
            "error": str(e)
        }