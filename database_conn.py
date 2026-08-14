import sqlite3
#C:\Users\yossi\Documents\AI Agents - Atlas\My_Python_Apps\simple_customers.db
#DB_NAME = 'C:\\Users\\yossi\\Documents\\AI Agents - Atlas\\My_Python_Apps\\CosmetiClinic.db'
import DLL_params as params

def get_connection():
    """יוצר ומחזיר חיבור לבסיס הנתונים."""
    return sqlite3.connect(params.DB_NAME)

def setup_database():
    """יוצר את טבלת התורים אם היא לא קיימת."""
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            service TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            client_Phone TEXT,
            is_deleted INTEGER DEFAULT 0
            )'''
        )
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments_repository (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date date NOT NULL,
            time TEXT NOT NULL,
            is_availeble INTEGER DEFAULT 1
            )'''
        )

    cursor.execute('''DROP VIEW IF EXISTS main.v_customers_data''')
    cursor.execute('''CREATE VIEW v_customers_data as
                        select client_phone
                        , max(client_name) as client_name
                        , date('now')as today,sum(case when is_deleted =0 and date < date('now') then 1 else 0 END) as total_visits
                        , max(case when is_deleted =0 and date < date('now') then date else NULL END) as last_visit
                        , max(case when is_deleted =0 and date >= date('now') then date else NULL END) as future_visit
                        FROM scheduled_appointments
                        group by client_phone''')

    cursor.execute('''CREATE TRIGGER IF NOT EXISTS appt_repository_updatedate
                    AFTER UPDATE ON appointments_repository
                    FOR EACH ROW
                    BEGIN
                    UPDATE appointments_repository 
                    SET update_date = datetime('now', 'localtime') 
                    WHERE rowid = NEW.rowid;
                    END''')
    cursor.execute('''CREATE TRIGGER IF NOT EXISTS update_scheduled_appt_date
                    AFTER UPDATE ON scheduled_appointments
                    FOR EACH ROW
                        BEGIN
                            UPDATE scheduled_appointments 
                            SET update_date = datetime('now', 'localtime') 
                            WHERE rowid = NEW.rowid;
                        END''')
    
    conn.commit()
    conn.close()
setup_database()

