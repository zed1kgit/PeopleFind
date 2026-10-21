from django.core.exceptions import PermissionDenied


class RoleRequiredMixin:
    """Пускает только пользователей с указанными ролями, иначе 403.

    Заменяет проверки request.user.role in (...), которые были скопированы
    в каждом view.
    """
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role not in self.allowed_roles:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
