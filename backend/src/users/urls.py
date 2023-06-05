from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, UserLoginAPIView, UserLogoutAPIView

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('users/set_password/',
         UserViewSet.as_view({'get': 'set_password'}),
         name='user-set-password'),
    path('auth/token/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('auth/token/logout/',
         UserLogoutAPIView.as_view(),
         name='user-logout'),
]
