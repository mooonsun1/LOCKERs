import MySQLdb

# MySQL 데이터베이스에 연결
connection = MySQLdb.connect(
    host='127.0.0.1',
    user='lockers',
    password='1111',
    database='locker_system',
    charset='utf8mb4'
)

try:
    with connection.cursor() as cursor:
        # 외래 키 제약 조건을 제거합니다.
        cursor.execute("ALTER TABLE django_admin_log DROP FOREIGN KEY django_admin_log_user_id_c564eba6_fk_login_user_id")
        connection.commit()
        print("Foreign key constraint removed successfully.")
except MySQLdb.Error as e:
    print(f"Error: {e}")
finally:
    connection.close()
