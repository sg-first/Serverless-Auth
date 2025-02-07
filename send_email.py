import hashlib

from email.message import EmailMessage
import smtplib
import ssl
from email.utils import formataddr
from .config import mail_server, nickname, mail_sender, mail_pswd

# MAX
max_email_length = 100
max_password_length = 100
# MIN
min_password_length = 6
verify_code_length = 6


# 发送验证码邮件
def send_email_verify(email, verify_code):
    # 收件人邮箱
    mail_receivers = email
    # 邮件主题
    mail_subject = '登录验证码'

    content = f"""您好，

注册验证码：{verify_code}（有效期五分钟）
为了保障您的账户安全，记得不要将验证码告诉别人。:D"""

    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = mail_subject
    msg["From"] = formataddr((nickname, mail_sender))
    msg["To"] = mail_receivers

    try:
        context = ssl.create_default_context()

        with smtplib.SMTP(mail_server, port=587) as smtp:
            smtp.starttls(context=context)
            smtp.login(mail_sender, mail_pswd)
            smtp.send_message(msg)
    except Exception as e:
        if str(e) == "(-1, b'\\x00\\x00\\x00')": # QQ邮箱的特殊响应格式
            print("邮件发送成功")
        else:
            print(f"发送验证码邮件失败: {str(e)}")
            raise e


# 以后可能用这个函数给用户批量发邮件
def send_email(email, mail_subject,
               html_content="<p>您好，這是邮箱测试功能</p>"):
    # 收件人邮箱
    mail_receivers = email

    msg = EmailMessage()
    # msg.set_content(content)  # 纯文本内容
    msg.add_alternative(html_content, subtype='html')  # HTML 内容
    msg["Subject"] = mail_subject
    msg["From"] = formataddr((nickname, mail_sender))
    msg["To"] = mail_receivers

    try:
        with smtplib.SMTP_SSL(mail_server, port=465) as smtp:
            smtp.login(mail_sender, mail_pswd)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(e)
        return False


# 加密密码
def encrypt_password(password):
    # 使用md5加密
    md5 = hashlib.md5()
    salt = "MLops-data".encode('utf-8')
    password = password.encode('utf-8')
    md5.update(password + salt)
    return md5.hexdigest()


# check lambdas
def check_space(s): return s.count(' ') == 0

def check_email(email): return all([
    len(email) <= max_email_length,
    check_space(email),
    email.count('@') == 1,
    email.count('.') == 1])
