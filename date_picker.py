import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
from datetime import date
import DLL_params as params

def get_date_from_popup():
    top = tk.Toplevel()
    top.title("בחירת תאריך לתור")
    top.attributes('-topmost', True)
    top.grab_set()
    
    today = date.today()
    
    cal = Calendar(
        top, 
        selectmode='day', 
        date_pattern='yyyy-mm-dd', 
        mindate=today 
    )
    cal.pack(pady=20, padx=20)
    
    # === שלב 1: עיצוב ויזואלי לתאריכים חסומים ===
    # נגדיר תגית חדשה בשם 'disabled' ונצבע את הרקע והטקסט שלה באפור
    cal.tag_config('disabled', background='#e0e0e0', foreground='#a0a0a0')
    
    # רשימת התאריכים הספציפיים שאנחנו רוצים לחסום (למשל, חגים או ימי חופש)
    # שים לב: אלה חייבים להיות אובייקטים מסוג date
    specific_disabled_dates = [
        date(2026, 8, 15),
        date(2026, 9, 20),
        date(2026, 10, 1)
    ]
    
    # עוברים על הרשימה ומוסיפים את התגית 'disabled' לכל אחד מהתאריכים בלוח השנה
    for disabled_date in specific_disabled_dates:
        cal.calevent_create(disabled_date, 'סגור', 'disabled')
        
    selected_date = [None]
    
    def on_select():
        selected_dt = cal.selection_get()
        
        # === שלב 2: מניעת הבחירה בפועל (לוגיקה) ===
        
        # 1. בדיקת ימי שבת
        if selected_dt.weekday() == 5:
            top.attributes('-topmost', False)
            messagebox.showerror("תאריך לא חוקי", "הקליניקה סגורה ביום שבת. אנא בחר יום אחר.")
            top.attributes('-topmost', True)
            return
            
        # 2. בדיקת תאריכים ספציפיים
        if selected_dt in specific_disabled_dates:
            top.attributes('-topmost', False)
            messagebox.showerror("תאריך תפוס", "הקליניקה סגורה בתאריך זה (חג/חופש). אנא בחר יום אחר.")
            top.attributes('-topmost', True)
            return
            
        # אם הכל תקין
        selected_date[0] = cal.get_date()
        top.destroy()
        
    btn = tk.Button(top, text="אשר תאריך", command=on_select, font=("Arial", 12))
    btn.pack(pady=10)
    
    top.wait_window()
    
    return selected_date[0]