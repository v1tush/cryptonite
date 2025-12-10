from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.edit import FormMixin

from ciphers.forms import CipherForm
from ciphers.models import Cipher, CipherLike
from logs.forms import SolutionLogForm
from logs.models import SolutionLog


class CreateEditCipher(LoginRequiredMixin, FormView):
    template_name = 'ciphers/create_cipher.html'
    form_class = CipherForm

    def dispatch(self, request, *args, **kwargs):
        self.cipher_id = kwargs.get('cipher_id')
        return super().dispatch(request, *args, **kwargs)

    def get_cipher(self):
        if self.cipher_id:
            return get_object_or_404(
                Cipher,
                pk=self.cipher_id,
                author=self.request.user,
            )

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
        context.update(
            {
                'title': 'Редактирование шифра'
                if is_edit
                else 'Создание нового шифра',
                'button_text': 'СОХРАНИТЬ ИЗМЕНЕНИЯ'
                if is_edit
                else 'СОЗДАТЬ ШИФР',
                'is_edit': is_edit,
            },
        )

        return context

    def form_valid(self, form):
        cipher = form.save(commit=False)
        cipher.author = self.request.user
        if self.cipher_id is None:
            cipher.cipher_type = 'community'

        cipher.save()
        return redirect(
            reverse_lazy(
                'users:profile',
                kwargs={'username': self.request.user.username},
            ),
        )

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


# TODO: исправить
class LibraryCommunityView(ListView):
    model = Cipher
    template_name = 'ciphers/libary.html'
    context_object_name = 'ciphers'
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cipher.objects.with_user_likes_and_approved(
                self.request.user,
            )

        return Cipher.objects.approved()


class LibraryCoursesView(ListView):
    model = Cipher
    template_name = 'ciphers/libary.html'
    context_object_name = 'ciphers'


class HideCipherView(LoginRequiredMixin, View):
    def post(self, request, cipher_id):
        cipher = get_object_or_404(Cipher, id=cipher_id, author=request.user)

        if cipher.status == 'pending' or cipher.status == 'rejected':
            return HttpResponseForbidden(
                'Нельзя скрыть шифр на модерации или заблокированный шифр',
            )

        cipher.status = 'hidden'
        cipher.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))


class OpenCipherView(LoginRequiredMixin, View):
    def post(self, request, cipher_id):
        cipher = get_object_or_404(Cipher, id=cipher_id, author=request.user)

        if cipher.status != 'hidden':
            return HttpResponseForbidden('Можно открыть только скрытые шифры')

        cipher.status = 'approved'
        cipher.save()
        return redirect(request.META.get('HTTP_REFERER', '/'))


class LikeCipherView(LoginRequiredMixin, View):
    def post(self, request, **kwargs):
        cipher = get_object_or_404(Cipher, pk=self.kwargs.get('cipher_id'))

        liked = False
        try:
            with transaction.atomic():
                like, created = CipherLike.objects.get_or_create(
                    user=request.user,
                    cipher=cipher,
                )
                if not created:
                    like.delete()
                else:
                    liked = True
        except IntegrityError:
            liked = True

        likes_count = CipherLike.objects.cipher_count_likes(cipher=cipher)

        return JsonResponse({'liked': liked, 'likes_count': likes_count})


# ! Реализация views для возможности решения
class SolveCipherView(FormMixin, DetailView):
    model = Cipher
    template_name = 'ciphers/solve.html'
    form_class = SolutionLogForm
    context_object_name = 'cipher'

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        return Cipher.objects.get(id=self.kwargs['cipher_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # базовый контекст
        context[
            'user_attempts'
        ] = SolutionLog.objects.user_solutions_for_cipher(
            self.request.user,
            self.get_object(),
        )
        return context

    def post(self, request, **kwargs):
        self.cipher = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        solution = form.save(commit=False)
        solution.cipher = self.cipher
        solution.user = self.request.user

        solution.correct = (
            solution.attempted_answer.strip()
            == self.cipher.answer_phrase.strip()
        )

        solution.save()

        return redirect(self.get_success_url())
