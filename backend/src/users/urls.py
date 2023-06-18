# users/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import UserLoginAPIView, UserLogoutAPIView, UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('set_password/', UserViewSet.as_view({'post': 'set_password'}),
         name='user-set-password'),
    path('auth/token/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('auth/token/logout/', UserLogoutAPIView.as_view(), name='user-logout'),
]
