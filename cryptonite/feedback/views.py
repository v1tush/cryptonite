import django.views.generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin

from ciphers.models import Cipher
from feedback.forms import FeedbackForm


class FeedbackView(
    LoginRequiredMixin,
    SingleObjectMixin,
    django.views.generic.FormView,
):
    form_class = FeedbackForm
    template_name = 'feedback/feedback.html'
    model = Cipher

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.author == request.user:
            raise PermissionDenied('Нельзя жаловаться на собственный шифр')

        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return get_object_or_404(Cipher, id=self.kwargs['cipher_id'])

    def get_success_url(self):
        cipher = self.get_object()
        return reverse('ciphers:solve_cipher', kwargs={'cipher_id': cipher.id})

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        cipher = self.get_object()
        feedback = form.save(commit=False)
        feedback.cipher = cipher
        feedback.author = self.request.user
        feedback.save()
        return super().form_valid(form)
