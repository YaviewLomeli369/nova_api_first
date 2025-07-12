# from rest_framework.permissions import BasePermission

# class HasCustomPermission(BasePermission):
#     def __init__(self, permiso):
#         self.permiso = permiso

#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.has_perm(self.permiso)

from rest_framework.permissions import BasePermission

class HasCustomPermission(BasePermission):
    def __init__(self, permiso):
        self.permiso = permiso

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm(self.permiso)


def CustomPermission(permiso_codename):
    class _CustomPermission(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.has_perm(permiso_codename)
    return _CustomPermission
