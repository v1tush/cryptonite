import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, Http404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.edit import FormMixin

from ciphers.forms import CipherForm
from ciphers.models import Cipher, CipherHelp, CipherLike, PurchasedHint
from logs.forms import SolutionLogForm
from logs.models import SolutionLog
from qr.utils import create_qr_for_cipher

HINT_PRICE = 100


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
        existing_hints = []
        if is_edit and self.cipher_id:
            cipher = self.get_cipher()
            existing_hints = cipher.hints.all().order_by('order')

        context.update(
            {
                'title': (
                    'Редактирование шифра'
                    if is_edit
                    else 'Создание нового шифра'
                ),
                'button_text': (
                    'СОХРАНИТЬ ИЗМЕНЕНИЯ' if is_edit else 'СОЗДАТЬ ШИФР'
                ),
                'is_edit': is_edit,
                'existing_hints': existing_hints,
            },
        )

        return context

    def form_valid(self, form):
        cipher = form.save(commit=False)
        cipher.author = self.request.user
        if self.cipher_id is None:
            cipher.cipher_type = 'community'

        cipher.status = 'pending'
        cipher.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'success': True,
                    'cipher_id': cipher.id,
                    'redirect_url': reverse_lazy(
                        'users:profile',
                        kwargs={'username': self.request.user.username},
                    ),
                },
            )

        return redirect(
            reverse_lazy(
                'users:profile',
                kwargs={'username': self.request.user.username},
            ),
        )

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'success': False,
                    'errors': form.errors,
                },
            )

        return self.render_to_response(self.get_context_data(form=form))


# TODO: исправить
class LibraryCommunityView(ListView):
    model = Cipher
    template_name = 'ciphers/library.html'
    context_object_name = 'ciphers'
    paginate_by = 20

    def get_queryset(self):
        approved = Cipher.objects.approved()
        if not self.request.user.is_authenticated:
            return approved

        return approved.with_user_likes_and_solutions(
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('rank', None)
        return context


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


class SolveCipherView(LoginRequiredMixin, FormMixin, DetailView):
    model = Cipher
    template_name = 'ciphers/cipher.html'
    form_class = SolutionLogForm
    context_object_name = 'cipher'

    def get_success_url(self):
        return self.request.path

    def get_object(self, queryset=None):
        cipher = get_object_or_404(Cipher, id=self.kwargs['cipher_id'])

        if (
            not self.request.user.is_staff
        ):  # иначе все ломается, когда нажимаю "проверить"
            if (
                cipher.status != 'approved'
                and cipher.author != self.request.user
            ):
                raise Http404()

        return cipher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # базовый контекст
        cipher = self.get_object()
        user = self.request.user
        hints = cipher.hints.all().order_by('order')
        purchased_hint_ids = PurchasedHint.objects.filter(
            user=user,
            hint__in=hints,
        ).values_list('hint_id', flat=True)
        purchased_hints = []
        available_hints = []
        for hint in hints:
            if hint.id in purchased_hint_ids:
                purchased_hints.append(
                    {
                        'id': hint.id,
                        'text': hint.text,
                        'order': hint.order,
                        'purchased': True,
                    },
                )
            else:
                available_hints.append(
                    {
                        'id': hint.id,
                        'order': hint.order,
                        'purchased': False,
                    },
                )

        context['purchased_hints'] = purchased_hints
        context['available_hints'] = available_hints
        context['hints_count'] = hints.count()
        context['user_balance'] = user.money
        context['hint_price'] = HINT_PRICE
        context['qr_code'] = create_qr_for_cipher(cipher, self.request)
        context[
            'user_attempts'
        ] = SolutionLog.objects.user_solutions_for_cipher(
            self.request.user,
            self.get_object(),
        )

        _lks_crs = CipherLike.objects.filter(
            user=self.request.user,
            cipher__pk=self.kwargs['cipher_id'],
        )

        context['likes_ciphers'] = (
            _lks_crs.first().cipher if _lks_crs.first() else None
        )

        context['last_attempt'] = SolutionLog.objects.get_last_attempt(
            self.request.user,
            self.object,
        )
        if context['last_attempt'] and self.object.attempt_limit is not None:
            context['left_attempt_cnt'] = (
                self.object.attempt_limit
                - context['last_attempt'].attempts_used
            )

        context['solved_users_cnt'] = SolutionLog.objects.get_solved_users_cnt(
            self.object,
        )
        context['top_users'] = SolutionLog.objects.get_top_solvers(
            self.get_object(),
        )
        context['has_limit'] = self.object.attempt_limit is not None
        return context

    def post(self, request, **kwargs):
        # Проверка модерации шифра
        self.object = self.get_object()

        if request.user.is_staff and 'moderation_action' in request.POST:
            action = request.POST.get('moderation_action')

            if self.object.status == 'pending':
                if action == 'approve':
                    self.object.status = 'approved'

                elif action == 'reject':
                    self.object.status = 'rejected'

                self.object.save()

            return redirect(request.path)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_hint_purchase(request)

        self.form = self.get_form()
        self.user = request.user

        if self.form.is_valid():
            last_attempt = SolutionLog.objects.get_last_attempt(
                self.user,
                self.object,
            )
            is_correct = last_attempt.correct if last_attempt else False
            if self.object.attempt_limit is not None:
                left_attempt_cnt = (
                    self.object.attempt_limit - last_attempt.attempts_used
                    if last_attempt
                    else self.object.attempt_limit
                )
            else:
                left_attempt_cnt = float('inf')

            if left_attempt_cnt <= 0 or is_correct:
                return self.form_invalid(self.form)

            return self.form_valid(self.form)

        return self.form_invalid(self.form)

    def handle_hint_purchase(self, request):
        try:
            data = json.loads(request.body)
            hint_id = data.get('hint_id')
            if not hint_id:
                return JsonResponse(
                    {
                        'success': False,
                    },
                )

            hint = get_object_or_404(CipherHelp, id=hint_id)
            user = request.user
            cipher = hint.cipher
            validation_error = self.validate_hint_purchase(user, cipher, hint)
            if validation_error:
                return validation_error

            user.money -= HINT_PRICE
            user.save()
            cipher.author.money += HINT_PRICE
            cipher.author.save()
            PurchasedHint.objects.create(
                user=user,
                hint=hint,
            )
            return JsonResponse(
                {
                    'success': True,
                    'message': 'Подсказка успешно куплена!',
                    'hint': {
                        'id': hint.id,
                        'text': hint.text,
                        'order': hint.order,
                    },
                    'new_balance': user.money,
                    'price_paid': HINT_PRICE,
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    'success': False,
                    'error': str(e),
                },
            )

    def validate_hint_purchase(self, user, cipher, hint):
        if user == cipher.author:
            return JsonResponse(
                {
                    'success': False,
                },
            )

        if PurchasedHint.objects.filter(user=user, hint=hint).exists():
            return JsonResponse(
                {
                    'success': False,
                },
            )

        if user.money < HINT_PRICE:
            return JsonResponse(
                {
                    'success': False,
                    'error': f'Недостаточно монет. Нужно {HINT_PRICE} монет',
                    'balance': user.money,
                    'required': HINT_PRICE,
                },
            )

        last_attempt = SolutionLog.objects.get_last_attempt(user, cipher)
        if last_attempt and last_attempt.correct:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Вы уже решили этот шифр',
                },
            )

        return None

    def form_valid(self, form):
        solution = form.save(commit=False)
        solution.cipher = self.object
        solution.user = self.request.user

        solution.correct = (
            solution.attempted_answer.strip()
            == self.object.answer_phrase.strip()
        )
        solution.save()
        if solution.correct:
            self.user.xp += 100
            self.user.money += 25
            solution.score = 100
            solution.save()
            self.user.save()

        return redirect(self.get_success_url())


class SaveCipherHintsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cipher_id = data.get('cipher_id')
            hints_data = data.get('hints', [])
            if not cipher_id:
                return JsonResponse(
                    {
                        'success': False,
                    },
                )

            cipher = get_object_or_404(
                Cipher,
                pk=cipher_id,
                author=self.request.user,
            )
            cipher.hints.all().delete()
            for hint_data in hints_data:
                CipherHelp.objects.create(
                    cipher=cipher,
                    text=hint_data.get('text', '').strip(),
                    order=hint_data.get('order'),
                )

            return JsonResponse(
                {
                    'success': True,
                    'hints_count': len(hints_data),
                },
            )

        except Exception as e:
            return JsonResponse(
                {
                    'success': False,
                    'error': str(e),
                },
            )
