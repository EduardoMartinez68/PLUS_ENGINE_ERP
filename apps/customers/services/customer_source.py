from ..models import CustomerSource
from django.http import JsonResponse
from ..plus_wrapper import Plus

def get_customer_source(user, query: str = "", quantity: int = 20) -> list:
    """
    Returns up to `quantity` CustomerSource records filtered by the query, if provided. 
    Only returns sources belonging to the user's company.

    Parameters:
    - user: The user performing the search (Django User object). 
    - query (str): Text to search for in the CustomerSource name. 
    - quantity (int): Maximum number of results to return. 

    Returns:
    - List[Dict[str, Any]]: A list of dictionaries containing the found CustomerSource records. Each dictionary contains:
        - id (int): The ID of the CustomerSource. 
        - name (str): The name of the CustomerSource. 
        - description (str): The description, empty if none exists. 
        - company (str | None): The company name, None if no company is associated.
    """
    
    # Filter by user's company and query, limit the number of results
    if query:
        sources = CustomerSource.objects.filter(
            company_id=user.company.id,
            name__icontains=query
        )[:quantity]
    else:
        sources = CustomerSource.objects.filter(
            company_id=user.company.id
        )[:quantity]

    # Format results
    result = [
        {
            "id": source.id,
            "name": source.name,
            "description": source.description or ""
        }
        for source in sources
    ]
    return result

def get_customer_source_select(user, query: str = "", quantity: int = 20) -> list:
    """
    Returns up to `quantity` CustomerSource records filtered by the query, if provided. 
    Only returns sources belonging to the user's company.

    Parameters:
    - user: The user performing the search (Django User object). 
    - query (str): Text to search for in the CustomerSource name. 
    - quantity (int): Maximum number of results to return. 

    Returns:
    - List[Dict[str, Any]]: A list of dictionaries containing the found CustomerSource records. Each dictionary contains:
        - id (int): The ID of the CustomerSource. 
        - name (str): The name of the CustomerSource. 
        - description (str): The description, empty if none exists. 
        - company (str | None): The company name, None if no company is associated.
    """
    
    # Filter by user's company and query, limit the number of results
    if query:
        sources = CustomerSource.objects.filter(
            company_id=user.company.id,
            name__icontains=query
        )[:quantity]
    else:
        sources = CustomerSource.objects.filter(
            company_id=user.company.id
        )[:quantity]

    # Format results
    result = [
        {
            "id": source.id,
            "text": source.name
        }
        for source in sources
    ]
    return result

def get_source_by_id(user, source_id: int, user_admin:str=None, password_admin:str=None) -> list:
    """
    Retrieve a CustomerSource by ID, only if it belongs to the user's company.

    Parameters:
    - user: The user performing the request (Django User object).
    - source_id (int): ID of the CustomerSource to retrieve.

    Returns:
    - Dict[str, Any]: Dictionary containing the result:
        - success (bool): True if found, False otherwise.
        - message (str): Descriptive message.
        - data (Dict[str, Any] | None): Information about the CustomerSource if found.
    """

    #first we will see if the user have the permission that need 
    has_perm, message = Plus.this_user_have_this_permission(user, 'see_customer_source', user_admin, password_admin)

    if not has_perm:
        return {"success": False, "message": message}
    
    try:
        source = CustomerSource.objects.get(id=source_id, company_id=user.company.id)
        result = {
            "success": True,
            "message": "CustomerSource retrieved successfully",
            "answer": {
                "id": source.id,
                "name": source.name,
                "description": source.description or ""
            }
        }
    except CustomerSource.DoesNotExist:
        result = {
            "success": False,
            "message": "CustomerSource not found in your company",
            "answer": None
        }
    except Exception as e:
        result = {
            "success": False,
            "message": f"Failed to retrieve CustomerSource: {str(e)}",
            "answer": None
        }

    return result

def add_a_new_source(user, name: str, description: str = "", user_admin:str=None, password_admin:str=None) -> list:
    """
    Create a new CustomerSource associated with the user's company.

    Parameters:
    - user: The user creating the CustomerSource (Django User object).
    - name (str): The name of the CustomerSource.
    - description (str): An optional description for the CustomerSource.

    Returns:
    - Dict[str, Any]: A dictionary containing information about the created CustomerSource or an error message.
        - success (bool): True if the creation was successful, False otherwise.
        - message (str): A descriptive message.
        - data (Dict[str, Any] | None): Information about the created CustomerSource if success is True.
    """

    #first we will see if the user have the permission that need 
    has_perm, message = Plus.this_user_have_this_permission(user, 'add_customer_source', user_admin, password_admin)

    if not has_perm:
        return {"success": False, "message": message}
    
    try:
        source = CustomerSource.objects.create(
            name=name.strip(),
            description=description.strip() if description else "",
            company_id=user.company.id 
        )
        result = {
            "success": True,
            "message": "CustomerSource created successfully",
            "data": {
                "id": source.id,
                "name": source.name,
                "description": source.description            
            }
        }
    except Exception as e:
        result = {
            "success": False,
            "error": f"Failed to create CustomerSource: {str(e)}",
            "data": None
        }
    return result

def update_source(user, source_id: int, name: str, description: str = "", user_admin:str=None, password_admin:str=None) -> list:
    """
    Edit a CustomerSource only if it belongs to the same company as the user. 

    Parameters:
    - user: The user performing the edit (Django User object). 
    - source_id (int): ID of the CustomerSource to edit. 
    - name (str): New name for the CustomerSource. 
    - description (str): Optional new description. 

    Returns:
    - Dict[str, Any]: Dictionary with the operation result:
    - success (bool): True if the edit was successful, False if an error occurred. 
    - message (str): Descriptive message. 
    - data (Dict[str, Any] | None): Information about the edited CustomerSource if success is True.
    """

    #first we will see if the user have the permission that need 
    has_perm, message = Plus.this_user_have_this_permission(user, 'update_customer_source', user_admin, password_admin)

    if not has_perm:
        return {"success": False, "message": message}
    
    try:
        # Retrieve only the sources belonging to the user's company
        source = CustomerSource.objects.get(id=source_id, company_id=user.company)

        # update all the field of the database
        source.name = name.strip()
        source.description = description.strip() if description else ""
        source.save()

        result = {
            "success": True,
            "message": "The source was update with success",
            "data": {
                "id": source.id,
                "name": source.name,
                "description": source.description
            }
        }
    except CustomerSource.DoesNotExist:
        result = {
            "success": False,
            "message": "message.not-exist-this-source-in-your-company",
            "data": None
        }
    except Exception as e:
        result = {
            "success": False,
            "error": f"Fail to update the customer: {str(e)}",
            "data": None
        }

    return result

def delete_a_source_with_his_id(user, source_id: int, user_admin:str=None, password_admin:str=None) -> list:
    """
    Deletes a CustomerSource only if it belongs to the user's company.

    Parameters:
    - user: The user performing the deletion (Django User object).
    - source_id (int): ID of the CustomerSource to delete.

    Returns:
    - Dict[str, Any]: Dictionary with the result of the operation:
        - success (bool): True if deleted successfully, False otherwise.
        - message (str): Descriptive message.
    """

    #first we will see if the user have the permission that need 
    has_perm, message = Plus.this_user_have_this_permission(user, 'delete_customer_source', user_admin, password_admin)

    if not has_perm:
        return {"success": False, "message": message}
    
    try:
        # Get the source only if it belongs to the user's company
        source = CustomerSource.objects.get(id=source_id, company_id=user.company)
        source.delete()
        result = {
            "success": True,
            "error": "CustomerSource deleted successfully"
        }
    except CustomerSource.DoesNotExist:
        result = {
            "success": False,
            "message": "CustomerSource not found in your company"
        }
    except Exception as e:
        result = {
            "success": False,
            "message": f"Failed to delete CustomerSource: {str(e)}"
        }

    return result