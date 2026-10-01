from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.views import redirect_to_login
from django.urls import reverse_lazy


class StaffRequiredMixin(AccessMixin):
    """Only active staff users may enter the management area; everyone else
    is sent to the manager's own login page (not the shop login)."""
    login_url = reverse_lazy('manager:login')

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not (user.is_authenticated and user.is_active and user.is_staff):
            return redirect_to_login(request.get_full_path(), self.login_url)
        return super().dispatch(request, *args, **kwargs)
