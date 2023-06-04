from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('', include('authentication.urls')),
    path('', include('users.urls')),
]
