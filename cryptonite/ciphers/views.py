from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
from django.views import View
from django.http import HttpResponseForbidden

from ciphers.forms import CipherForm
from ciphers.models import Cipher


class CreateEditCipher(LoginRequiredMixin, FormView):
    template_name = 'ciphers/create_cipher.html'
    form_class = CipherForm

    def dispatch(self, request, *args, **kwargs):
        self.cipher_id = kwargs.get('cipher_id')
        return super().dispatch(request, *args, **kwargs)

    def get_cipher(self):
        if self.cipher_id:
            return get_object_or_404(Cipher, pk=self.cipher_id, author=self.request.user)
        return Cipher()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_cipher()
        kwargs['create_flag'] = self.cipher_id is None
        if self.request.method == 'GET':
            kwargs['data'] = None
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        is_edit = self.cipher_id is not None
        context.update({
            'title': 'Редактирование шифра' if is_edit else 'Создание нового шифра',
            'button_text': 'СОХРАНИТЬ ИЗМЕНЕНИЯ' if is_edit else 'СОЗДАТЬ ШИФР',
            'is_edit': is_edit,
        })
        return context

    def form_valid(self, form):
        cipher = form.save(commit=False)
        cipher.author = self.request.user
        if self.cipher_id is None:
            cipher.cipher_type = 'community'
        cipher.save()
        return redirect(
            reverse_lazy('users:profile', kwargs={'username': self.request.user.username})
        )

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


# TODO: исправить
class LibraryCommunityView(ListView):
    model = Cipher
    template_name = 'ciphers/libary.html'
    context_object_name = 'ciphers'


class LibraryCoursesView(ListView):
    model = Cipher
    template_name = 'ciphers/libary.html'
    context_object_name = 'ciphers'


class HideCipherView(LoginRequiredMixin, View):
    def post(self, request, cipher_id):
        cipher = get_object_or_404(Cipher, id=cipher_id, author=request.user)

        if cipher.status == "pending":
            return HttpResponseForbidden("Нельзя скрыть шифр на модерации")

        cipher.status = "hidden"
        cipher.is_published = False
        cipher.save()
        return redirect(request.META.get("HTTP_REFERER", "/"))

class OpenCipherView(LoginRequiredMixin, View):
    def post(self, request, cipher_id):
        cipher = get_object_or_404(Cipher, id=cipher_id, author=request.user)

        if cipher.status != "hidden":
            return HttpResponseForbidden("Можно открыть только скрытые шифры")

        cipher.status = "approved"
        cipher.is_published = True
        cipher.save()
        return redirect(request.META.get("HTTP_REFERER", "/"))


# ! Реализация views для возможности решения
