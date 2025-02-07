import psycopg2
from django.http import JsonResponse

db_conn = None

def initDB():
    global db_conn
    try:
        # 连接到数据库
        db_conn = psycopg2.connect(
            database="postgres",
            user="user",
            password="password",
            host="host.sql.tencentcdb.com",
            port=20649,
        )
        return True
    except psycopg2.OperationalError as e:
        # 如果连接数据库失败，打印错误信息并返回False
        print(f"Error while connecting to PostgreSQL (OperationalError): {e}")
        return False
    except psycopg2.Error as e:
        # 如果其他数据库操作失败，打印错误信息并返回False
        print(f"Error while connecting to PostgreSQL (Error): {e}")
        return False

initDB()


def exec_sql(func):
    if db_conn is None:
        return JsonResponse({"error": "数据库连接失败"}, status=500)
    try:
        db_cur = db_conn.cursor()
        return func(db_cur)
    except Exception as e:
        db_conn.rollback()
        db_cur.close()
        return JsonResponse({'error': str(e)}, status=500)
