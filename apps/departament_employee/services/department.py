from django.db.models import Q
from ..plus_wrapper import Plus
from core.models import UserDepartment

def search_department_for_filter(user, search=None, activated=None, limit=20):
    try:
        # --- 1. limit first to the user's company ---
        qs = UserDepartment.objects.filter(id_company=user.company)

        # --- 2. filter by activated ---
        qs = qs.filter(activated=Plus.to_bool(activated))


        # --- 3. apply search filter ---
        if search and search.strip():
            qs = qs.filter(
                Q(name__icontains=search.strip())
            )

        # --- 4. limit results ---
        qs = qs.order_by("name")[:limit]

        # --- 5. format the response ---
        departments = []
        for d in qs:
            departments.append({
                "id": d.id,
                "name": d.name,
                "description": d.description or "",
                "color": d.color or "#6C63FF",
                "activated": "active" if d.activated else "inactive",
                "company": {
                    "id": d.id_company.id if d.id_company else None,
                    "name": d.id_company.name if d.id_company else None,
                } if d.id_company else None,
            })

        return {"success": True, "answer": departments, "error": None}

    except Exception as e:
        return {"success": False, "answer": [], "error": str(e)}
