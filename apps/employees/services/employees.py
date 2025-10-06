from ..plus_wrapper import Plus
from core.models import CustomUser
from django.core.paginator import Paginator
from django.db.models import Q

def get_employees_for_search(company, branch=None, sku=None, activated=None, page=1, limit=20):
    """
    Obtiene empleados filtrados por empresa, sucursal, nombre similar, estado activo, rol o departamento.
    Devuelve los primeros 20 resultados por página.
    """

    # Base query: siempre filtra por empresa
    query = CustomUser.objects.filter(company=company)

    # Filtra por sucursal si se proporciona
    if branch:
        query = query.filter(branch=branch)

    # Filtro por activo/inactivo
    if activated is not None:
        activated = Plus.to_bool(activated)
        query = query.filter(is_active=activated)

    # Búsqueda por nombre aproximado (case-insensitive)
    if sku:
        query = query.filter(username__icontains=sku)

    # Solo los campos que realmente importan (para performance)
    query = query.select_related('user_role', 'user_department', 'branch')

    # Ordenar por nombre (más profesional)
    query = query.order_by('username')

    # Paginación: 20 por página
    paginator = Paginator(query, limit)
    employees_page = paginator.get_page(page)

    # Transformar a datos limpios y seguros
    results = []
    for emp in employees_page:
        department_data = None
        if emp.user_department:
            department_data = {
                "name": emp.user_department.name,
                "color": emp.user_department.color,
                "description": emp.user_department.description,
            }

        role_data = None
        if emp.user_role:
            role_data = {
                "name": emp.user_role.name,
                "description": emp.user_role.description,
            }

        branch_data = None
        if emp.branch:
            branch_data = {
                "id": emp.branch.id,
                "name": emp.branch.name_branch,
                "nickname": emp.branch.nickname,
                "email": emp.branch.email_branch,
                "phone": emp.branch.phone,
                "country": emp.branch.country,
            }

        results.append({
            "id": emp.id,
            "avatar": emp.avatar.url if emp.avatar else '/static/img/profile-employees.webp',
            "name": emp.name or '',
            "username": emp.username or '',
            "email": emp.email or '',
            "cellphone": emp.cellphone or '',
            "phone": emp.phone or '',
            "branch": branch_data["name"] if branch_data else '',
            "department": department_data["name"] if department_data else '',
            "department_color": department_data["color"] if department_data and department_data.get("color") else '#075FAC',
            "role": role_data["name"] if role_data else '',
            "is_active": emp.is_active,
        })

    return {
        "success": True,
        "answer": results,
        "error": '',
        "page": employees_page.number,
        "total_pages": paginator.num_pages,
        "total_employees": paginator.count
    }
