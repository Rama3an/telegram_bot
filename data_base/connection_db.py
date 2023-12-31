import pymysql.cursors
from data_base.config import host, user, password, db_name

try:
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
except Exception as e:
    print("Fail", e)
