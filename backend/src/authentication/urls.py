from django.urls import path, include

urlpatterns = [
    path('auth/token/', include('djoser.urls.authtoken')),
]
