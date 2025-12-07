from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
import django.views.generic

import ciphers.forms
import ciphers.models


class CreateEditCipher(LoginRequiredMixin, django.views.generic.FormView):
    template_name = 'ciphers/create_cipher.html'
    form_class = ciphers.forms.CipherForm
    success_url = reverse_lazy('users:profile')

    def dispatch(self, request, *args, **kwargs):
        self.cipher_id = kwargs.get('cipher_id')
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.cipher_id:
            cipher = get_object_or_404(
                ciphers.models.Cipher,
                pk=self.cipher_id,
                author=self.request.user,
            )
            kwargs['instance'] = cipher
            kwargs['create_flag'] = False
        else:
            kwargs['instance'] = ciphers.models.Cipher(
                author=self.request.user,
            )
            kwargs['create_flag'] = True

        kwargs['author'] = self.request.user
        if self.request.method == 'GET':
            kwargs['data'] = None

        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        if self.cipher_id:
            cipher = get_object_or_404(
                ciphers.models.Cipher,
                pk=self.cipher_id,
                author=self.request.user,
            )
            initial.update(
                {
                    'title': cipher.title,
                    'encrypted_phrase': cipher.encrypted_phrase,
                    'answer_phrase': cipher.answer_phrase,
                    'description': cipher.description,
                    'difficulty': cipher.difficulty,
                    'attempt_limit': cipher.attempt_limit,
                },
            )

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.cipher_id:
            context['title'] = 'Редактирование шифра'
            context['button_text'] = 'СОХРАНИТЬ ИЗМЕНЕНИЯ'
            context['is_edit'] = True
        else:
            context['title'] = 'Создание нового шифра'
            context['button_text'] = 'СОЗДАТЬ ШИФР'
            context['is_edit'] = False

        return context

    def form_valid(self, form):
        form.save()
        return redirect(self.success_url)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


# ! Реализация views для возможности рещения
