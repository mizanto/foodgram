from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TagViewSet

app_name = 'recipes'

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]
