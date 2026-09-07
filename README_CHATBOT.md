# 🤖 מערכת צ'אט-בוט חכם לניהול תורים לקליניקה (Full-Stack Web App)

הרחבה וובית מלאה למערכת ניהול התורים של קליניקת "יופי טופי".
המערכת משלבת שרת API מבוסס **FastAPI**, ממשק צ'אט וובי מבוסס **Streamlit** התומך ב-RTL (עברית), ומנוע AI מבוסס **Gemini 2.5 Flash** עם תמיכה ב-**Tool Calling (Function Calling)** לשליפת נתונים מתוך מסד הנתונים SQLite.

---

## 🏗️ מבנה הרכיבים והקבצים החדשים

### 1. `api_server.py` (שרת ה-Backend & AI Engine)
שרת מרכזי שנבנה ב-FastAPI וממלא שני תפקידים עיקריים:
* **חשיפת אנדפוינטים לנתונים (REST API):**
  * `GET /api/customers/search/{name}`: בדיקה האם לקוח קיים במערכת לפי שם בטבלה/תצוגה `v_customers_data`.
  * `GET /api/appointments/{client_phone}`: שליפת כל התורים המוזמנים של הלקוח מ-`scheduled_appointments` בפורמט JSON.
* **ניהול שיחת ה-AI מול Gemini:**
  * מקבל את היסטוריית השיחה מ-`app.py` באנדפוינט `POST /api/chat`.
  * מגדיר את ה-Tools עבור Gemini (`check_customer_by_name` ו-`get_appointments_by_phone`).
  * מנהל את השרשרת של ה-Function Calling (קריאה ראשונה ל-Gemini ➔ הפעלת הפונקציה המקומית ➔ החזרת התוצאה ל-Gemini ➔ יצירת תשובה סופית בשפה טבעית).

### 2. `app.py` (ממשק ה-Frontend בצ'אט - Streamlit)
ממשק משתמש וובי נקי ומעוצב ללקוחות הקצה:
* **תמיכה מלאה ב-RTL:** כולל הזרקת CSS מותאם אישית המיישר את בועות הצ'אט, חלון הקלט, הפונטים והאייקונים לימין.
* **ניהול זיכרון שיחה (`st.session_state`):** שומר על היסטוריית השיחה הרציפה.
* **מנגנון הגנת עומס (Timeout):** שולח בקשות B2B מול ה-API עם טיימאאוט ומציג הודעות שגיאה אדיבות בעברית במידה ושיחה נתקעת או שרת ה-API אינו זמין.

### 3. `logger.py` (מנגנון התיעוד)
רכיב אחראי על מעקב ותיעוד שאילתות מסד הנתונים:
* תופס כל קריאה של `cursor.execute` ומקבל את פקודת ה-SQL ואת הפרמטרים שנשלחו.
* רושם אוטומטית שורת לוג עם חותמת זמן (Timestamp) לקובץ `log.txt`.

### 4. `chatbot_service.py` (פונקציות ה-Tools)
מכיל את פונקציות העזר המגדירות את הקריאות הפנימיות ל-API:
* `check_customer_by_name(name)`: מתקשרת מול האנדפוינט החיפושי ומחזירה תגובת JSON.
* `get_appointments_by_phone(client_phone)`: מתקשרת מול אנדפוינט התורים ומחזירה JSON של התורים המתוכננים.

### 5. קובץ ה-`.env` (ניהול אבטחה ומפתחות)
קובץ סודי המשמש לאחסון משתני סביבה.
* **תכולה:**
  ```env
  GEMINI_API_KEY=your_actual_gemini_api_key_here
  ```
* **חשיבות:** שומר על מפתח ה-API מחוץ לקוד המקור כך שלא ייחשף במאגרי קוד כמו GitHub.

---

## 🛠️ דרישות מוקדמות והתקנת ספריות

יש לוודא שהותקנו כל הספריות הנדרשות לפרויקט:

```bash
pip install fastapi uvicorn streamlit google-genai requests python-dotenv
```

---

## 🚀 הוראות הפעלה מפורטות (שלב אחר שלב)

כדי להריץ את האפליקציה בצורה תקינה יש להפעיל **שני טרמינלים נפרדים במקביל**:

### שלב 1: הגדרת מפתח ה-API
ודא שקיים קובץ `.env` בתיקיית השורש של הפרויקט המכיל את מפתח ה-Gemini שלך:
```env
GEMINI_API_KEY=sk-xxxx-YOUR-API-KEY-HERE
```

### שלב 2: הרצת שרת ה-Backend (FastAPI)
פתח **טרמינל ראשון**, נווט לתיקיית הפרויקט והרץ:

```bash
uvicorn api_server:app --reload
```
* השרת יעלה ויקשיב לכתובת: `http://localhost:8000`
* ניתן לצפות בתיעוד ה-API האוטומטי בכתובת: `http://localhost:8000/docs`

### שלב 3: הרצת ממשק ה-Frontend (Streamlit)
פתח **טרמינל שני**, נווט לתיקיית הפרויקט והרץ:

```bash
streamlit run app.py
```
* חלון הדפדפן ייפתח אוטומטית בכתובת: `http://localhost:8501`
* כעת תוכל להתכתב עם הצ'אט-בוט בשפה טבעית!

---

## 📝 מעקב ולוגים
כל פניה של הבוט למסד הנתונים SQLite תתועד באופן אוטומטי בקובץ `log.txt` בפורמט הבא:
```text
[2026-09-06 15:30:12] SQL: SELECT client_name FROM v_customers_data WHERE client_name LIKE ? LIMIT 1 | Params: ('%דני%',)
[2026-09-06 15:30:25] SQL: SELECT id, client_name, service, date, time, status FROM scheduled_appointments WHERE client_phone = ? | Params: ('0501234567',)
```
