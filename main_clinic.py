import DLL_params
import database_conn
import appointment_manager
import date_picker 
import pool_inventory
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
from DLL_params import services 

#from bidi.algorithm import get_display # Hebrew text display

def is_future(date_str, time_str):
    """מוודא שהתאריך והשעה נמצאים בעתיד"""
    full_date_str = f"{date_str} {time_str}"
    try:
        appt_time = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        appt_time = datetime.strptime(full_date_str, "%y-%m-%d %H:%M")
    return appt_time > datetime.now()

class ClinicApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מערכת ניהול תורים קליניקה - יופי טופי")
        # מנסה להגדיל את החלון למקסימום בהתאם למערכת ההפעלה
        try:
            self.root.state('zoomed')  # מתאים ל-Windows
        except tk.TclError:
            self.root.attributes('-zoomed', True)  # מתאים ל-Mac/Linux

        # כותרת ראשית
        title_lbl = tk.Label(root, text="מערכת ניהול הקליניקה - יופי טופי", font=("Arial", 18, "bold"))
        title_lbl.pack(pady=20)
        
        # יצירת הכפתורים לתפריט הראשי

        btn_add = tk.Button(root, text="קביעת תור חדש", command=self.add_appt, font=("Arial", 14), width=20, bg="#99e9ff")
        btn_add.pack(pady=10)
        
        btn_update = tk.Button(root, text="עדכון תור קיים", command=self.update_appt, font=("Arial", 14), width=20, bg="#99e9ff")
        btn_update.pack(pady=10)
        
        btn_delete = tk.Button(root, text="ביטול תור", command=self.delete_appt, font=("Arial", 14), width=20, bg="#99e9ff")
        btn_delete.pack(pady=10)

        btn_view   = tk.Button(root, text="צפייה בכל התורים", command=self.view_appts, font=("Arial", 14), width=20, bg="#99e9ff")
        btn_view.pack(pady=10)

        btn_custlist = tk.Button(root, text="צפייה בפרטי לקוחות", command=self.view_customers, font=("Arial", 14), width=20, bg="#99e9ff")
        btn_custlist.pack(pady=10)
        
        btn_exit = tk.Button(root, text="יציאה", command=root.quit, font=("Arial", 14), width=20, bg="#ff9999")
        btn_exit.pack(pady=20) 

    def add_appt(self):
        # פותח את טופס יצירת התור
        self.open_form_window("קביעת תור חדש", is_update=False)

    def update_appt(self):
        # מבקש תחילה את מזהה התור שרוצים לעדכן
        appt_id = simpledialog.askinteger("עדכון תור", "הכנס מזהה של התור לעדכון")
        if appt_id:
            # Fetch existing data from the database
            existing_data = appointment_manager.get_appointment_by_id(appt_id)
            if not existing_data:
                messagebox.showerror("שגיאה", "לא נמצא תור עם מזהה זה.", parent=self.root)
                return False
            
            appt_date, appt_time = existing_data[2], existing_data[3]
            # you dont know if the update involves time slot change, so we release the slot temporarily
            appointment_manager.release_repository_slot_temporary(appt_date, appt_time)             
            self.open_form_window("עדכון תור", is_update=True, appt_id=appt_id, existing_data=existing_data)

    def view_appts(self):
        appointments = appointment_manager.get_all_appointments()
        if not appointments:
            messagebox.showinfo("תורים", "אין תורים קבועים כרגע.", parent=self.root)
            return
        
        # בניית מחרוזת של כל התורים להצגה בפופ-אפ
        text = ""
        for appt in appointments:
            text += f"ID: {appt[0]} | שם: {appt[1]} | טיפול: {appt[2]} | תאריך: {appt[3]} | שעה: {appt[4]}\n"
        #messagebox.showinfo("רשימת התורים", text, parent=self.root)
        self.show_custom_message("רשימת התורים", text)

    def view_customers(self):
        customers = appointment_manager.get_all_customers()
        if not customers:
            messagebox.showinfo("לקוחות ", "אין לקוחות פעילים כרגע.", parent=self.root)
            return
        
        # בניית מחרוזת של כל הלקוחות להצגה בפופ-אפ
        text = ""
        for customer in customers:
            text += f"phone : {customer[0]} | name: {customer[1]} | total visits : {customer[3]} |  future visit : {customer[5]}\n"
        #messagebox.showinfo("רשימת הלקוחות", text, parent=self.root)
        self.show_custom_message("רשימת הלקוחות", text)

    def delete_appt(self):
        appt_id = simpledialog.askinteger("ביטול תור", "הכנס מזהה של התור לביטול:")
        if appt_id:
            # Fetch existing data from the database
            existing_data = appointment_manager.get_appointment_by_id(appt_id)
            if not existing_data:
                messagebox.showerror("שגיאה", "לא נמצא תור עם מזהה זה.", parent=self.root)
            #   return False
            else: 
                appointment_manager.delete_appointment(appt_id)
                messagebox.showinfo("הצלחה", "!התור בוטל בהצלחה", parent=self.root)

    # Update the function signature to accept existing_data

    def open_form_window(self, title, is_update, appt_id=None, existing_data=None):
        form = tk.Toplevel(self.root)
        form.title(title)
        # Remove the geometry line and add this instead:
        try:
            form.state('zoomed')  # Works on Windows
        except tk.TclError:
            form.attributes('-zoomed', True)  # Fallback for Linux/Mac
        form.attributes('-topmost', True) 

        def pick_date():
                    selected = date_picker.get_date_from_popup()
                    if selected:
                        date_var.set(selected)
                        available_times = appointment_manager.get_available_times_for_date(selected)
                        
                        menu = time_menu["menu"]
                        menu.delete(0, "end") 
                        
                        if not available_times:
                            time_var.set("אין שעות פנויות")
                            messagebox.showinfo("תפוס", "אין שעות פנויות בתאריך זה, אנא בחר יום אחר.", parent=form)
                        else:
                            time_var.set(available_times[0])
                            for t in available_times:
                                menu.add_command(label=t, command=tk._setit(time_var, t))
        
        
        # --- שדה שם ---
        tk.Label(form, text=":שם הלקוח/ה").pack(pady=(10, 0))
        name_var = tk.StringVar()
        name_entry = tk.Entry(form, textvariable=name_var, justify="right")
        name_entry.pack()
        
        # --- שדה טיפול ---
        tk.Label(form, text=":בחר סוג טיפול").pack(pady=(10, 0))
        service_var = tk.StringVar(form)
        service_var.set(services[0]) 
        tk.OptionMenu(form, service_var, *services).pack()

        tk.Button(form, text="בחר תאריך", command=pick_date).pack(pady=(0, 10))
        
        # --- שדה תאריך ---
        #tk.Label(form, text="תאריך:").pack(pady=(10, 0))
        date_var = tk.StringVar()
        tk.Label(form, textvariable=date_var, fg="blue", font=("Arial", 10, "bold")).pack()
        
        # --- שדה שעה ---
        tk.Label(form, text=":שעת טיפול").pack(pady=(10, 0))
        time_var = tk.StringVar()
        time_var.set("ממתין לבחירת תאריך") 
        time_menu = tk.OptionMenu(form, time_var, "")
        time_menu.pack()

        # --- שדה טלפון ---
        tk.Label(form, text=":מספר טלפון").pack(pady=(10, 0))
        client_phone_var = tk.StringVar()
        tk.Entry(form, textvariable=client_phone_var, justify="center").pack()
                        
        

        # --- טעינת נתונים קיימים (במקרה של עדכון) ונעילת השם ---
        if is_update and existing_data:
            exist_name, exist_service, exist_date, exist_time, exist_client_phone= existing_data
            name_var.set(exist_name)
            service_var.set(exist_service)
            date_var.set(exist_date)
            time_var.set(exist_time)
            client_phone_var.set(exist_client_phone)
            name_entry.config(state="disabled") # נעילת שדה השם
            
            available_times = appointment_manager.get_available_times_for_date(exist_date)
            if exist_time not in available_times:
                available_times.append(exist_time)
                available_times.sort()
                
            menu = time_menu["menu"]
            menu.delete(0, "end")
            for t in available_times:
                menu.add_command(label=t, command=tk._setit(time_var, t))
                
            time_var.set(exist_time)


        # --- פונקציית השמירה הפנימית ---
        def save():
            name = name_var.get()
            service = service_var.get()
            date = date_var.get()
            time = time_var.get()
            client_phone = client_phone_var.get()  # Get the phone number from the input field
            # בדיקה שכל השדות תקינים
            if not name or not date or not client_phone or time == "בחר תאריך תחילה" or time == "אין שעות פנויות":
                messagebox.showerror("שגיאה", "יש למלא את כל השדות ולוודא שנבחר תאריך ושעה.", parent=form)
                return
            
            if not is_future(date, time):
                messagebox.showerror("שגיאה", "לא ניתן לקבוע תור לתאריך או שעה בעבר.", parent=form)
                return
                
            # קריאה ל-appointment_manager לביצוע במסד הנתונים
            if is_update:
                appointment_manager.update_appointment(appt_id, name, service, date, time, client_phone_var.get())
            else:
                appointment_manager.add_appointment(name, service, date, time, client_phone_var.get())
            
            # במקרה שאתה בתוך הפונקציה open_form_window, החלון שלך נקרא form
            messagebox.showinfo("!הצלחה", "התור נשמר בהצלחה במערכת.", parent=form)
            form.destroy()
            
        # ==========================================
        # זה הכפתור שהיה חסר! יצירה והצגה שלו בתחתית הטופס
        # ==========================================
        btn_text = "עדכן תור" if is_update else "שמור תור חדש"
        tk.Button(form, text=btn_text, command=save, bg="lightgreen", font=("Arial", 12, "bold")).pack(pady=20)


    def show_custom_message(self, title, message):
        """חלון הודעה מותאם אישית שניתן לשנות את גודלו"""
        msg_box = tk.Toplevel(self.root)
        msg_box.title(title)
        
        # כאן אתה קובע את הגודל המדויק! (רוחב x גובה)
        msg_box.geometry("800x600") 
        
        msg_box.attributes('-topmost', True)
        
        # נועל את החלון הראשי כדי שהמשתמש יחויב ללחוץ "אישור"
        msg_box.grab_set() 
        
        # התווית עם הטקסט - כאן אפשר לשנות את גודל הפונט
        lbl = tk.Label(msg_box, text=message, font=("Arial", 14, "bold"))
        lbl.pack(expand=True, fill='both', pady=20)
        
        # כפתור אישור לסגירת החלון
        btn = tk.Button(msg_box, text="אישור", command=msg_box.destroy, 
                        font=("Arial", 12), bg="lightblue", width=10)
        btn.pack(pady=15)

if __name__ == "__main__":
    # ודא שמסד הנתונים קיים לפני טעינת החלון
    database_conn.setup_database()
    # ודא השלמת תורים - שנה קדימה
    pool_inventory.populate_availability_pool()
    # הפעלת הממשק הגרפי
    root = tk.Tk()
    app = ClinicApp(root)
    root.mainloop()