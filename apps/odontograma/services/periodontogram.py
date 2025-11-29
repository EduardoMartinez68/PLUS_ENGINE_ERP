from ..models import HistoryOdontogram, Odontogram

def update_periodontogram_service(periodontogram_id, data, user):
    
    try:
        odontogram = Odontogram.objects.get(id=periodontogram_id)
    except Odontogram.DoesNotExist:
        return {
            "success": False,
            "message": "Periodontogram not found",
            "answer": [],
            "error": "No periodontogram with the given ID exists."
        }
    
    latest_history = HistoryOdontogram.objects.filter(
        customer=odontogram.customer,
    ).order_by('-created_at').first()

    if not latest_history:
        return {
            "success": False,
            "message": "No history found for the given odontogram",
            "answer": [],
            "error": "No history records exist for this odontogram."
        }
    

    try:
        # Update the periodontograma field with the new data
        latest_history.periodontograma = data
        latest_history.save()
        
        return {
            "success": True,
            "message": "Periodontogram updated successfully",
            "answer": [],
            "error": ""
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Error updating periodontogram",
            "answer": [],
            "error": str(e)
        }