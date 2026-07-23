from django.db.models import Q
from core.Plus import Plus
from core.models import CustomUser
def search_users_in_company(user, search_name=None, limit=20):
    try:

        # -----------------------------------
        # BASE QUERY
        # -----------------------------------

        qs = CustomUser.objects.filter(
            company=user.company,
            branch=user.branch,
            is_active=True
        ).order_by('-date_joined')[:200]  # safety limit

        result = []

        # -----------------------------------
        # NORMALIZE SEARCH
        # -----------------------------------

        query = (search_name or '').lower().strip()

        # -----------------------------------
        # FILTER IN PYTHON
        # -----------------------------------

        for u in qs:

            real_name = (u.name or '').lower()

            # Search by real name
            if query and query not in real_name:
                continue

            result.append({
                "id": u.id,
                "text": u.name,
                "photo": u.avatar.url if u.avatar else '/static/img/employees-select.webp',
            })

            # -----------------------------------
            # LIMIT RESULTS
            # -----------------------------------

            if len(result) >= limit:
                break

        return {
            "success": True,
            "answer": result,
            "error": None
        }

    except Exception as e:

        return {
            "success": False,
            "answer": [],
            "error": str(e)
        }