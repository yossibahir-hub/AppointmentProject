# chatbot_service.py
import requests

def get_appointments_by_phone(client_phone: str) -> dict:
    """קריאה פנימית ל-API לשליפת התורים"""
    try:
        response = requests.get(f"http://localhost:8000/api/appointments/{client_phone}")
        if response.status_code == 200:
            return response.json()
        return {"status": "not_found", "message": "לא נמצאו תורים רשומים למספר זה."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# הגדרת ה-Tool עבור ה-LLM
tools = [
    {
        "name": "get_appointments_by_phone",
        "description": "Fetches all scheduled appointments for a client using their phone number.",
        "parameters": {
            "type": "object",
            "properties": {
                "client_phone": {
                    "type": "string",
                    "description": "The client's phone number, e.g., 0501234567"
                }
            },
            "required": ["client_phone"]
        }
    }
]