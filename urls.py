from django.urls import path
from .config import is_rsa
from . import views

if is_rsa:
    urlpatterns = [
        path("check_email/", views.check_email_by_rsa, name="check_email"),
        path("check_login/", views.check_token_by_rsa, name="check_login"),
    ]
else:
    urlpatterns = [
        path("check_email/", views.check_email_by_sql, name="check_email"),
        path("check_login/", views.check_token_by_sql, name="check_login"),
    ]

urlpatterns += [
    path("send_verify_code_to_email/", views.send_verify_code_to_email, name="send_verify_code_to_email"),
]
