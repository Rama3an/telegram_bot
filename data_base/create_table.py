from data_base.connection_db import connection

try:
    with connection.cursor() as cursor:
        table = ("CREATE TABLE IF NOT EXISTS Paper "
                 "(id INT PRIMARY KEY AUTO_INCREMENT,"
                 "telegram_id INT,"
                 "paper VARCHAR(255));")
        cursor.execute(table)
    print("Success")
except Exception as e:
    print("Fail", e)