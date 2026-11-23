from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.views.generic import ListView

from ciphers.models import Cipher


class UserPassesTestForStaffMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('main:main')


class StaffNotificationsView(
    LoginRequiredMixin,
    UserPassesTestForStaffMixin,
    ListView,
):
    model = Cipher
    template_name = 'notifications/staff_page.html'
    context_object_name = 'ciphers'

    def get_queryset(self):
        return Cipher.objects.pending().with_user_likes_and_solutions(
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
