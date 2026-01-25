from django.db.models import Q
from ..plus_wrapper import Plus
from core.models import CustomUser

def search_users_in_company(user, search_name=None, limit=20):
    try:
        # 1. Filtrar por company y branch + usuarios activos
        qs = CustomUser.objects.filter(
            company=user.company,
            branch=user.branch,
            is_active=True
        )

        # 2. Si hay búsqueda por nombre, aplicar filtro
        if search_name:
            search_name = search_name.lower()
            qs = qs.filter(username__icontains=search_name).order_by('-date_joined')[:limit]
        else:
            # 3. Si no hay búsqueda, obtener los 20 más recientes
            qs = qs.order_by('-date_joined')[:limit]

        # 4. Formatear la respuesta
        users = []
        for u in qs:
            users.append({
                "id": u.id,
                "text": u.username,
                "photo": u.avatar.url if u.avatar else '/static/img/employees-select.webp',
            })

        return {"success": True, "answer": users, "error": None}

    except Exception as e:
        return {"success": False, "answer": [], "error": str(e)}