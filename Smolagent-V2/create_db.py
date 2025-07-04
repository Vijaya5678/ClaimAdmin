# 📁 File: database/create_hospital_db.py

import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

# Create the hospital table
cursor.execute('''
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY,
    patient_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    amount REAL NOT NULL
)
''')

# Dummy data: 10 patient records
data = [
    (1, "Alice Smith", 60, "Female", "Hypertension", 15400.00),
    (2, "John Doe", 45, "Male", "Diabetes", 12600.50),
    (3, "Robert Black", 70, "Male", "Cardiac Arrest", 22400.00),
    (4, "Lucy Green", 30, "Female", "Asthma", 9800.00),
    (5, "Emma Brown", 55, "Female", "Arthritis", 11200.75),
    (6, "David White", 65, "Male", "Kidney Stones", 13850.25),
    (7, "Sophia Blue", 40, "Female", "Thyroid", 8900.00),
    (8, "Michael Gray", 75, "Male", "Stroke", 25600.90),
    (9, "Lily Turner", 50, "Female", "Migraine", 7200.60),
    (10, "James Clark", 35, "Male", "Fracture", 10100.30)
]

# Insert data into the table
cursor.executemany('''
INSERT OR REPLACE INTO patients 
(patient_id, patient_name, age, gender, diagnosis, amount)
VALUES (?, ?, ?, ?, ?, ?)
''', data)

# Commit changes and close
conn.commit()
conn.close()

print("✅ Hospital database created and populated with 10 patients.")
