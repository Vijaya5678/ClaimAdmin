import sqlite3

def show_all_hospital_data():
    conn = sqlite3.connect('hospital_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hospital_data")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No data found.")
    else:
        print("Hospital Data:")
        for row in rows:
            print({
                "incident_id": row[0],
                "patient_name": row[1],
                "policy_num": row[2],
                "admitted": row[3],
                "discharged": row[4],
                "bill": row[5],
            })

if __name__ == "__main__":
    show_all_hospital_data()
