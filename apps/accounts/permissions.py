from rest_framework.permissions import BasePermission, SAFE_METHODS




class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Admin"


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "Agent"

