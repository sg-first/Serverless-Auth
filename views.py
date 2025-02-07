# 发送验证码的接口
import time
import hashlib
import base64
import requests
import datetime
from . import PGDB
from . import libs
from . import config
from .send_email import send_email_verify, check_email
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from django.http import JsonResponse


def send_verify_code_to_email(request):
    try:
        uid = request.GET.get("uid")
        if not check_email(uid):
            return JsonResponse({"error": "邮箱格式不正确"})
        else:
            code = generate_verify_code(uid)
            # 发送邮件
            send_email_verify(uid, code)
            return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"error": str(e)})


def check_email_inner(request, success_continuation):
    uid = request.GET.get("uid") # 邮箱
    if not check_email(uid):
        return JsonResponse({"error": "邮箱格式不正确"})
    else:
        code = request.GET.get("code") # 验证码
        if verify_code(uid, code):    
            return success_continuation(uid)
        else:
            return JsonResponse({"error": "验证码不正确"})


# 原地验证
def check_email_by_rsa(request):
    return check_email_inner(request, libs.get_token_by_rsa)


# 数据库验证
def check_email_by_sql(request):
    return check_email_inner(request, libs.get_token_by_sql)



# 原地验证
def check_token_by_rsa(request):
    uid = request.GET.get('uid')
    token = request.GET.get('token')
    try:
        data = libs.decrypt(token)
        if data[0] != uid:
            return JsonResponse({"error": "uid不正确"})
        else:
            if datetime.datetime.now().timestamp() > float(data[1]):
                return JsonResponse({"error": "token已过期"})
            else:
                return JsonResponse({"message": "ok"})
    except:
        return JsonResponse({"error": "token不正确"})



# 非原地验证
def check_token_by_sql(request):
    uid = request.GET.get('uid')
    token = request.GET.get('token')
    def inner(db_cur):
        # 1.查找token是否正确
        db_cur.execute(f"SELECT expiration_time FROM {config.token_table} WHERE uid = %s AND token = %s", (uid, token,))
        result = db_cur.fetchone()

        if result is None:
            # 判断uid是否存在
            db_cur.execute(f"SELECT * FROM {config.user_table} WHERE uid = %s", (uid,))
            uid_exists = db_cur.fetchone()
            if uid_exists is None:
                return JsonResponse({"error": "uid不存在"})
            else:
                return JsonResponse({"error": "token不正确"})

        if result[0] < datetime.datetime.now():
            return JsonResponse({"error": "token已过期"})
        else:
            return JsonResponse({"message": "ok"})
    return PGDB.exec_sql(inner)


def generate_verify_code(email):
    """
    生成验证码
    :param email: 邮箱
    :return: 验证码
    """
    # 获取当前时间戳并转换为15分钟时间段序号
    current_slot = int(time.time()) // config.verify_expire_time
    # 组合邮箱和时间段序号
    raw_data = f"{email}:{current_slot}".encode('utf-8')
    # 使用AES加密
    cipher = AES.new(config.verify_key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(raw_data, AES.block_size))
    encrypted = base64.b64encode(encrypted).decode('ascii')
    # 取encrypted的第1，3，5位，与encrypted的最后三位拼起来
    code = encrypted[0] + encrypted[2] + encrypted[4] + encrypted[-3:]
    return code
    

def verify_code(email, code):
    """
    验证验证码
    :param email: 邮箱
    :param code: 用户输入的验证码
    :return: 是否有效
    """
    if len(code) != 6:
        return False
    try:
        return generate_verify_code(email) == code
        
    except Exception:
        return False