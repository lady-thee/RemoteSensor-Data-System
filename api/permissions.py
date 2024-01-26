from rest_framework.permissions import BasePermission


class IsOperator(BasePermission):
    def has_permission(self, request, view):
        # if request.user.is_superuser:
        #     return request.user 
        return request.user.role == 'operator' or (request.user.is_superuser)
    
    