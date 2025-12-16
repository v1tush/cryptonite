from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.shortcuts import redirect

import ciphers.models


class UserPassesTestMixinForStaff(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('main:main')


# Занимался только по части стафа
class StaffNotificationsView(
    LoginRequiredMixin,
    UserPassesTestMixinForStaff,
    ListView,
):
    model = ciphers.models.Cipher
    template_name = 'ciphers/library.html'
    context_object_name = 'ciphers'
    
    def get_queryset(self):
        if self.request.user.is_staff:
            unchecked = ciphers.models.Cipher.objects.pending()
            return unchecked
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context