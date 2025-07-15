from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'



class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'manager'


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'client'


class IsRider(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in [ 'driver', 'partner_rider']
    

class IsPartnerPickup(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'partner_shop'
    

class IsVerifiedPartner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['partner_rider', 'partner_shop'] and request.user.is_verified


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access only to the owner of the object or an admin.
    Useful for object-level permissions.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin' or obj.created_by == request.user