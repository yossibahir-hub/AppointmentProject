DB_NAME = 'CosmetiClinic.db'
get_all_appointments_query = 'SELECT * FROM scheduled_appointments WHERE is_deleted = 0 ORDER BY date asc, time asc'
#get_all_customers_query = 'SELECT client_phone, client_name, COUNT(*) as visit_count FROM scheduled_appointments WHERE is_deleted = 0 GROUP BY client_phone, client_name'
get_all_customers_query = 'SELECT * FROM v_customers_data'


# רשימת הטיפולים - תשמש אותנו בתוך התפריט הנפתח ב-GUI
services = [
    "טיפול פנים",
    "הסרת שיער בלייזר",
    "עיצוב גבות",
    "מניקור ופדיקור",
    "איפור קבוע"
]