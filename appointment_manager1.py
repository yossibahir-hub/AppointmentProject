import sqlite3
from database_conn import DB_NAME

def add_appointment(client_name, service, date, time, client_phone):
    conn = sqlite3.Connection(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO scheduled_appointments (client_name, service, date, time, client_Phone)
        VALUES (?, ?, ?, ?, ?)
    ''', (client_name, service, date, time, client_phone))
    cursor.execute('''
            update appointments_repository set is_availeble=0 where date = ? and time = ?
        ''', (date, time))
    conn.commit()
    conn.close()

def get_all_appointments():
    conn = sqlite3.Connection(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scheduled_appointments WHERE is_deleted = 0 ORDER BY date, time')
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_appointment(appt_id, client_name, service, date, time):
    conn = sqlite3.Connection(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE scheduled_appointments
        SET client_name = ?, service = ?, date = ?, time = ?
        WHERE id = ?
    ''', (client_name, service, date, time, appt_id))
    conn.commit()
    conn.close()

def delete_appointment(appt_id):
    conn = sqlite3.Connection(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE scheduled_appointments SET is_deleted = 1 WHERE id = ?', (appt_id,))
    conn.commit()
    conn.close()

def is_time_slot_available(date, time, exclude_appt_id=None):
    """בודק אם קיים תור בתאריך ובשעה שסופקו."""
    conn = sqlite3.Connection(DB_NAME)
    cursor = conn.cursor()
    
    if exclude_appt_id:
        # בדיקה במקרה של עדכון תור: התעלם מהתור הנוכחי
        cursor.execute('''
            SELECT id FROM scheduled_appointments 
            WHERE date = ? AND time = ? AND id != ?
        ''', (date, time, exclude_appt_id))
    else:
        # בדיקה רגילה במקרה של קביעת תור חדש
        cursor.execute('''
            SELECT id FROM scheduled_appointments 
            WHERE date = ? AND time = ?
        ''', (date, time))
        
    existing_appointment = cursor.fetchone()
    conn.close()
    
    # הפונקציה תחזיר True אם לא נמצא תור חופף (כלומר, המשבצת פנויה)
    return existing_appointment is None

def get_available_times_for_date(selected_date):
    """Fetches all available time slots for a specific date from the repository."""
    conn = sqlite3.Connection(DB_NAME)
    cursor = conn.cursor()
    
    # Note: Assuming your column is named is_availeble 
    cursor.execute('''
        SELECT time FROM appointments_repository 
        WHERE date = ? AND is_availeble = 1
        ORDER BY time
    ''', (selected_date,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # rows is a list of tuples like: [('09:00',), ('10:00',)]
    # We convert it to a simple flat array: ['09:00', '10:00']
    available_times = [row[0] for row in rows]
    
    return available_times