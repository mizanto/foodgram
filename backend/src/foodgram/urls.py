from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/recipes/', include('recipes.urls')),
    path('api/users/', include('users.urls')),
]
