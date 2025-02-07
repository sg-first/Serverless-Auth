import rsa
from . import config
import random
import hashlib
import datetime
from . import PGDB
from django.http import JsonResponse

# 生成指定长度的随机验证码
def random_code(length):
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    result = ""
    for _ in range(length):
        index = random.randint(0, 9)
        result += chars[index]
    return result


def generate_token(uid):
    random_seed = random_code(3)  # 生成三位随机数字
    input_data = uid + random_seed
    m = hashlib.md5()  # 初始化md5对象
    m.update(input_data.encode("utf8"))  # 对字符串进行 UTF-8 编码后更新 md5 对象
    return m.hexdigest()  # 返回 MD5 哈希值的十六进制表示

def encrypt(uid):
    outtime = datetime.datetime.now() + datetime.timedelta(days=14)
    timestamp = outtime.timestamp()
    strtime = str(timestamp)
    return rsa.encrypt(f'{uid}|{strtime}'.encode(), config.encrypt_key).hex()

def decrypt(token):
    return rsa.decrypt(bytes.fromhex(token), config.decrypt_key).decode().split('|')

def get_token_by_rsa(uid):  # 应该有uid
    def inner(db_cur):
        db_cur.execute(f"INSERT INTO {config.user_table} (uid) VALUES (%s) ON CONFLICT (uid) DO NOTHING", (uid,))
        PGDB.db_conn.commit()
        return JsonResponse({'token': encrypt(uid)})
    return PGDB.exec_sql(inner)


def get_token_by_sql(uid):
    def inner(db_cur):
        # 获取当前时间，+14天（有效期）
        timestamp = datetime.datetime.now() + datetime.timedelta(days=14)

        db_cur.execute(f"SELECT token FROM {config.token_table} WHERE uid = %s", (uid,))
        token = db_cur.fetchone()
        if token:
            # token，更新对应的token的有效时长
            db_cur.execute(f"UPDATE {config.token_table} SET expiration_time = %s WHERE uid = %s", (timestamp, uid,))
            PGDB.db_conn.commit()
            return JsonResponse({'token': token})
        else:
            # 如果token不存在，说明对应的uid并未注册，则先在user_table插入uid
            db_cur.execute(f"INSERT INTO {config.user_table} (uid) VALUES (%s) ON CONFLICT (uid) DO NOTHING", (uid,))
            # 随后生成并插入token
            token = generate_token(uid)
            db_cur.execute(f"INSERT INTO {config.token_table} (uid, token, expiration_time) VALUES (%s, %s, %s)", (uid, token, timestamp,))
            PGDB.db_conn.commit()
            return JsonResponse({'token': token})
    return PGDB.exec_sql(inner)
