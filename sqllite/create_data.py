import sqlite3

# Connect (or create) SQLite database file
conn = sqlite3.connect('hospital_data.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS hospital_data (
    id TEXT PRIMARY KEY,
    patient_name TEXT NOT NULL,
    policy_num TEXT NOT NULL,
    admission_date TEXT NOT NULL,
    discharge_date TEXT NOT NULL,
    hospital_bill REAL NOT NULL
)
''')

# Data to insert
data = [
    ("IND-2025-0001", "Alice Smith", "PN-12312312", "2025-03-15", "2025-03-20", 4700),  # Bill different from claim INC-2025-0001 (4500)
    ("IND-2025-0004", "Bob Johnson", "PN-45645645", "2025-04-01", "2025-04-10", 5400),  # Bill matches claim INC-2025-0004 (5400)
]

# Insert data
cursor.executemany('''
INSERT OR REPLACE INTO hospital_data (id, patient_name, policy_num, admission_date, discharge_date, hospital_bill)
VALUES (?, ?, ?, ?, ?, ?)
''', data)

# Commit and close
conn.commit()
conn.close()

print("Hospital data inserted successfully.")
