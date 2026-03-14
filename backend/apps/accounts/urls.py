from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register', views.register, name='auth-register'),
    path('login', views.login, name='auth-login'),
    path('me', views.me, name='auth-me'),
    path('profile', views.profile_update, name='auth-profile'),
    path('users/search', views.search_users, name='auth-users-search'),
    path('users/online', views.online_users, name='auth-users-online'),
    path('users', views.list_users, name='auth-users-list'),
    path('token/refresh', TokenRefreshView.as_view(), name='token-refresh'),
]
