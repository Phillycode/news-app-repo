from rest_framework import permissions


class IsReaderOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow readers to perform certain actions.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        # Write permissions only for readers
        return request.user.is_authenticated and request.user.role == "reader"


class IsJournalistOrPublisher(permissions.BasePermission):
    """
    Custom permission to only allow journalists or publishers
    to perform certain actions.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [
            "journalist",
            "publisher",
            "editor",
        ]


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        # This assumes the model has a 'user' field or similar
        if hasattr(obj, "user"):
            return obj.user == request.user
        elif hasattr(obj, "journalist") and hasattr(obj.journalist, "user"):
            return obj.journalist.user == request.user

        return False
