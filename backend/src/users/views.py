from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import check_password
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription
from .paginators import UsersPaginator
from .serializers import (SetPasswordSerializer, UserLoginSerializer,
                          UserRegisterSerializer, UserSerializer)
from users.serializers import UserSubscriptionSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UsersPaginator

    def get_permissions(self):
        if self.action in ['create', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        return super().get_serializer_class()

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False,
            methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            current_password_valid = check_password(
                serializer.validated_data.get('current_password'),
                request.user.password
            )
            if not current_password_valid:
                return Response({"current_password": ["Wrong password."]},
                                status=status.HTTP_400_BAD_REQUEST)
            request.user.set_password(
                serializer.validated_data.get('new_password'))
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            following__user=request.user).order_by('username')
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = UserSubscriptionSerializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriptionSerializer(
            subscriptions, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],
            url_path='subscribe')
    def subscribe(self, request, pk=None):
        if request.method == 'POST':
            return self._add_subscription(request, pk)
        elif request.method == 'DELETE':
            return self._remove_subscription(request, pk)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def _add_subscription(self, request, pk=None):
        user_to_subscribe = self.get_object()

        _, created = Subscription.objects.get_or_create(
            user=request.user, author=user_to_subscribe)

        if created:
            return Response({"detail": "Successfully subscribed."},
                            status=status.HTTP_201_CREATED)

        return Response({"detail": "You are already subscribed to this user."},
                        status=status.HTTP_400_BAD_REQUEST)

    def _remove_subscription(self, request, pk=None):
        user_to_unsubscribe = self.get_object()
        subscription = Subscription.objects.filter(
            user=request.user, author=user_to_unsubscribe).first()

        if subscription:
            subscription.delete()
            return Response({"detail": "Successfully unsubscribed."},
                            status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "You are not subscribed to this user."},
                        status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(email=serializer.validated_data['email'],
                            password=serializer.validated_data['password'])

        if user is not None:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"auth_token": token.key}, status=200)
        return Response({"detail": "Invalid credentials"}, status=400)


class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=204)
