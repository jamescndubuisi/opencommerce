from django.urls import path
from .views import login_page, homepage, sign_up
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login', login_page, name='log_in'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('', homepage, name="home"),
    path('register', sign_up, name="register"),
]
