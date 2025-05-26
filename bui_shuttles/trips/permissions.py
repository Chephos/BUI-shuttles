from bui_shuttles.users import permissions as user_permissions

class IsOwner(user_permissions.IsDriver):
    def has_object_permission(self, request, view, obj):
        if super().has_object_permission(request, view, obj):
            return obj.driver == request.user.driver
        return False