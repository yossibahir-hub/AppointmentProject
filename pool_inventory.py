# This script populates, on system start, the availability pool up to 365 days of time slots (10:00 to 19:00) for a clinic. It generates the data and inserts it into the SQLite database efficiently using executemany.

import sqlite3
from datetime import datetime, timedelta
import DLL_params as params

def populate_availability_pool():
    conn = sqlite3.connect(params.DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute("SELECT coalesce(max(date), date('now')) as maxdate FROM appointments_repository")
    max_date = cursor.fetchone()  # Type of max_date[0] = class 'str' (e.g., '2026-08-15') 
    
    # 1. Generate the data
    Maxdate = datetime.strptime(max_date[0], "%Y-%m-%d").date()
    print(f"Max date in appointments_repository: {Maxdate}")
    slots = []
    # Loop through 365 days
    for day_offset in range(365):
        add_date = today + timedelta(days=day_offset)
        #print(f"Type of add_date: {type(add_date)}")
        #print(f"Add date being processed: {add_date}")
        date_str = add_date.strftime("%Y-%m-%d")
        # Loop through 24 hours (0 to 23)
        
        if add_date > Maxdate: # Only add slots for dates beyond the current max date in the database
            print(f"Generating slots for date: {add_date} when max date is {max_date[0]}")
            for hour in range(10, 20):  # Assuming the clinic operates from 10:00 to 19:00
                time_str = f"{hour:02d}:00"  # Formats single digits with a leading zero (e.g., "09:00")
                slots.append((date_str, time_str))
    # 2. Insert the data into SQLite efficiently
    # executemany is much faster than running 8,760 separate INSERT statements
    cursor.executemany('''
        INSERT INTO appointments_repository (date, time)
        VALUES (?, ?)
    ''', slots)
    conn.commit()
    print(f"Successfully inserted {len(slots)} time slots into the pool!")
    conn.close()


