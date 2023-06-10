from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an object to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
