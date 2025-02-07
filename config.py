import rsa
import os

is_rsa = True
user_table = "user"
current_dir = os.path.dirname(os.path.abspath(__file__))

# is_rsa = True（原地鉴权模式）需要配置以下项
encrypt_key = rsa.PublicKey.load_pkcs1(open(os.path.join(current_dir, 'encrypt_key.pem')).read().encode())
decrypt_key = rsa.PrivateKey.load_pkcs1(open(os.path.join(current_dir, 'decrypt_key.pem')).read().encode())
# is_rsa = False（数据库鉴权模式）需要配置以下项
token_table = "public.token"

# 加密密钥 (16字节)
verify_key = b'YourrrrVerifyKey'
# 过期时间（秒数）
verify_expire_time = 15 * 60

# 邮件服务器
mail_server = 'smtp.qq.com'
# 发件人昵称
nickname = 'nickname'
# 发件人邮箱
mail_sender = 'mail_sender@foxmail.com'
# 发件人邮箱密码
mail_pswd = 'mail_pswd'