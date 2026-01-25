from ..plus_wrapper import Plus
from core.models import Branch
from django.core.paginator import Paginator
from django.db.models import Q



def get_information_of_the_branch(company, name=None, page=1, limit=20):
    """
    Obtains information about a company's branches.
    If a name is provided, filters by partial matches (case-insensitive).
    Returns the first 'limit' results per page in alphabetical order.
    """

    # first we will to filter all the branch for the company and that be activate
    query = Branch.objects.filter(company=company, activated=True)
 
    #Filter by partial name if provided
    if name:
        query = query.filter(name_branch__icontains=name)

    # Sort alphabetically by branch name
    query = query.order_by('name_branch')

    # Pagination
    paginator = Paginator(query, limit)
    branches_page = paginator.get_page(page)

    # Transform to clean data 
    results = []
    for branch in branches_page:
        results.append({
            "id": branch.id,
            "text": branch.name_branch or "",
            "name": branch.name_branch or "",
            "nickname": branch.nickname or "",
            "email": branch.email_branch or "",
            "phone": branch.phone or "",
            "cellphone": branch.cellphone or "",
            "country": branch.country or "",
            "address": branch.address or "",
            "website": branch.website or "",
            "activated": branch.activated,
        })

    return {
        "success": True,
        "answer": results,
        "error":'',
        "page": branches_page.number,
        "total_pages": paginator.num_pages,
        "total_branches": paginator.count
    }