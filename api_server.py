import sqlite3
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from DLL_params import DB_NAME
import logger

# טעינת המשתנים מתוך קובץ ה-.env
load_dotenv()
app = FastAPI()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') 
client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# 1. Endpoints של בסיס הנתונים (API)
# ---------------------------------------------------------

@app.get("/api/appointments/{client_phone}")
def get_appointments(client_phone: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = '''
        SELECT id, client_name, service, date, time 
         FROM scheduled_appointments 
         WHERE is_deleted=0 AND client_phone = ?
    '''
    params = (client_phone,)
    
    # Executing and logging in one step
    logger.execute_and_log(cursor, query, params)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        raise HTTPException(status_code=404, detail="לא נמצאו תורים למספר זה.")
        
    appointments = [
        {"appointment_id": r[0], "client_name": r[1], "service": r[2], "date": r[3], "time": r[4]}
        for r in rows
    ]
    return {"client_phone": client_phone, "appointments": appointments}

# def get_appointments(client_phone: str):
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
    
#     cursor.execute('''
#         SELECT id, client_name, service, date, time 
#         FROM scheduled_appointments 
#         WHERE is_deleted=0 AND client_phone = ?
#     ''', (client_phone,))

#     # Executing and logging in one step
#     execute_and_log(cursor, query, params)
#     rows = cursor.fetchall()
#     conn.close()
    
#     if not rows:
#         raise HTTPException(status_code=404, detail="לא נמצאו תורים למספר זה.")
        
#     appointments = [
#         {"appointment_id": r[0], "client_name": r[1], "service": r[2], "date": r[3], "time": r[4], "status": r[5]}
#         for r in rows
#     ]
#     return {"client_phone": client_phone, "appointments": appointments}


@app.get("/api/customers/search/{name}")
def search_customer_by_name(name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    query = '''
        SELECT client_name 
        FROM v_customers_data 
        WHERE client_name LIKE ?
        LIMIT 1
    '''
    params = (f"%{name}%",)
    
    # Executing and logging in one step
    logger.execute_and_log(cursor, query, params)
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="לקוח לא נמצא.")
        
    return {"found": True, "client_name": row[0]}
# def search_customer_by_name(name: str):
#     """מחפשת שם לקוח בטבלת/תצוגת v_customers_data"""
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
    
#     # חיפוש גמיש (כיסוי לשמות חלקיים או דומים)
#     cursor.execute('''
#         SELECT client_name 
#         FROM v_customers_data 
#         WHERE client_name LIKE ?
#         LIMIT 1
#     ''', (f"%{name}%",))
    
#     row = cursor.fetchone()
#     conn.close()
    
#     if not row:
#         raise HTTPException(status_code=404, detail="לקוח לא נמצא.")
        
#     return {"found": True, "client_name": row[0]}


# ---------------------------------------------------------
# 2. הגדרת פונקציות ה-Tools עבור Gemini
# ---------------------------------------------------------

def check_customer_by_name(name: str) -> str:
    """Checks if a client's name exists in the clinic system (v_customers_data).
    
    Args:
        name: The client's full or first name mentioned in the message.
    """
    try:
        res = requests.get(f"http://localhost:8000/api/customers/search/{name}", timeout=5)
        if res.status_code == 200:
            return json.dumps(res.json(), ensure_ascii=False)
        return json.dumps({"found": False, "message": "שם הלקוח לא נמצא במערכת."})
    except Exception as e:
        return json.dumps({"found": False, "error": str(e)})


def get_appointments_by_phone(client_phone: str) -> str:
    """Fetches all scheduled appointments for a client using their phone number.
    
    Args:
        client_phone: The client's phone number as a string (e.g., '0501234567').
    """
    try:
        res = requests.get(f"http://localhost:8000/api/appointments/{client_phone}", timeout=5)
        if res.status_code == 200:
            return json.dumps(res.json(), ensure_ascii=False)
        return json.dumps({"error": "לא נמצאו תורים למספר זה."})
    except Exception as e:
        return json.dumps({"error": str(e)})


# מיפוי שמות הפונקציות לפונקציות בפועל
tools_map = {
    "check_customer_by_name": check_customer_by_name,
    "get_appointments_by_phone": get_appointments_by_phone
}


# ---------------------------------------------------------
# 3. Chat Endpoint
# ---------------------------------------------------------

class ChatPayload(BaseModel):
    messages: list

@app.post("/api/chat")
def chat_endpoint(payload: ChatPayload):
    # System Instruction מעודכן המציב את שלבי הזיהוי
    sys_instruction = (
        "אתה עוזרת (אישה) וירטואלית של קליניקת קוסמטיקה. תפקידך לעזור ללקוחות לקבל מידע על התורים שלהם.\n"
        "פעלי לפי השלבים הבאים:\n"
        "1. אם הלקוח מציין את שמו, השתמשי ב-tool `check_customer_by_name` כדי לבדוק אם הוא קיים במערכת.\n"
        "2. אם השם נמצא, עני בסגנון: 'שלום לך <client_name>, מצאתי אותך במערכת, אנא הכנס מספר נייד לטובת זיהוי'.\n"
        "3. ברגע שהלקוח מספק מספר טלפון, השתמשי ב-tool `get_appointments_by_phone` כדי לשלוף את פרטי התורים ולהציג אותם בצורה ברורה.\n"
        "4. אם השם או הנייד לא נמצאו, יש לענות בצורה אדיבה ולבקש ממנו לבדוק שוב את הפרטים."
    )

    contents = []
    for msg in payload.messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=msg["content"])]
            )
        )

    # העברת שני ה-Tools בתוך הקונפיגורציה
    config = types.GenerateContentConfig(
        system_instruction=sys_instruction,
        tools=[check_customer_by_name, get_appointments_by_phone],
        temperature=0.2
    )

    # קריאה ראשונה ל-Gemini
    response = client.models.generate_content(
        model="gemini-3.7-flash",

        contents=contents,
        config=config
    )

    # טיפול בהפעלת Tools במידה וג'מיני החליט לקרוא לאחד מהם
    if response.function_calls:
        contents.append(response.candidates[0].content)
        
        function_responses = []
        for call in response.function_calls:
            func = tools_map.get(call.name)
            if func:
                result = func(**call.args)
            else:
                result = json.dumps({"error": "Function not found"})

            function_responses.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result}
                )
            )

        contents.append(types.Content(parts=function_responses))

        # קריאה שנייה לניסוח תשובה אנושית סופית
        final_response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=contents,
            config=config
        )
        return {"response": final_response.text}

    return {"response": response.text}