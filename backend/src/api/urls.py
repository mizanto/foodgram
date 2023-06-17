from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserLoginAPIView, UserLogoutAPIView, UserViewSet

app_name = 'api'

# не до конца понял коментарий, если ты имел в виду формирование всех путей
# в приложении api (так было в теории), то вот обновленная версия, если что-то
# другое, то поясни подробнее, не знаю какую сюда еще логику можно вынести :)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('users/set_password/',
         UserViewSet.as_view({'post': 'set_password'}),
         name='user-set-password'),
    path('auth/token/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('auth/token/logout/',
         UserLogoutAPIView.as_view(), name='user-logout'),
]
