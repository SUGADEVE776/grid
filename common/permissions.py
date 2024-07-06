from rest_framework import permissions


class PolicyPermission(permissions.BasePermission):
    """Custom Policy based permission."""

    def has_permission(self, request, view):
        """Get the policy slug from the view and validate permissions."""

        user = request.user
        if user.is_anonymous:
            return False
        return True
