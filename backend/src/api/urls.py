from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('auth/', include('authentication.urls')),
    path('', include('users.urls')),
]
