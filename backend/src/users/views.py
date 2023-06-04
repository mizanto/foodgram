from rest_framework.response import Response
from rest_framework import status
from djoser.views import UserViewSet as DefaultUserViewSet
from .serializers import UserCreateSerializer


class CustomUserViewSet(DefaultUserViewSet):
    serializer_class = UserCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        # Do not include the 'password' field in the response.
        data = {
            'email': user.email,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }

        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

# Create your views here.

# list of users: GET /users/
# register a new user: POST /users/
# user profile: GET /users/{id}/
# current user profile: GET /users/me/
# change password: POST /users/set_password/
# authorization: POST /auth/token/login/
# logout: POST /auth/token/logout/
