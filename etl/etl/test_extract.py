import psycopg2

try:
    connection = psycopg2.connect(
        dbname='eeg_database',
        user='admin',
        password='css222',
        #รันนอก docker ใช้ localhost
        host='localhost',
        port='5432'
    )

    cursor = connection.cursor()


    query ="""
        SELECT * FROM eeg_data where eeg_id = 1;
        """
    cursor.execute(query)
    connection.commit() 
    rows = cursor.fetchall()

    print(rows[0])
    # print("สร้าง teble แล้ว")

except Exception as e:
    print(f"เกิดข้อผิดพลาด: {e}")

finally:
    if connection:
        cursor.close()
        connection.close()
