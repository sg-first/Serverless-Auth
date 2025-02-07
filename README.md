# ms-Auth

## 数据库
### 网络配置
需要数据库所在地域放通数据库的外网端口
### 建表
```sql
CREATE TABLE {token_table} (
    uid VARCHAR(255) PRIMARY KEY REFERENCES public.{user_table}(uid),  -- 设置外键引用 public.user_character
    token CHAR(32) NOT NULL,  -- token字段，固定长度32的字符串
    expiration_time TIMESTAMP NOT NULL  -- 过期时间字段，不带时区信息的TIMESTAMP
);
```
AIhuman和taskWorld有两个参数不同，具体看下面

## py服务配置
### 安装SDK
#### 云服务安装sdk
P.S：https://console.cloud.tencent.com/scf/list?rid=16&ns=default
1. 先创建一个Django模板云函数，创建完毕后从git拉取项目，进入项目目录后执行python cloudDeployment.py
2. 进入djangodemo，打开settings.py，将第46行`'django.middleware.csrf.CsrfViewMiddleware'`注释掉
3. 回到src目录
4. `pip install pycryptodome -t .`
5.  部署
