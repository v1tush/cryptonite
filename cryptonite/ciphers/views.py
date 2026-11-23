import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.http import (
    Http404,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import DetailView, FormView, ListView
from django.views.generic.edit import FormMixin

from ciphers.constants import HINT_PRICE
from ciphers.forms import CipherForm
from ciphers.models import Cipher, CipherHelp, CipherLike, PurchasedHint
from ciphers.services import (
    GameRuleError,
    moderate_cipher,
    purchase_hint,
    save_cipher_hints,
    submit_solution,
    visible_ciphers,
)
from feedback.models import Feedback
from logs.forms import SolutionLogForm
from logs.models import SolutionLog
from qr.models import QR


def _read_json(request):
    try:
        data = json.loads(request.body)
    except (ValueError, RecursionError):
        raise ValueError('Ожидается JSON-объект') from None
    if not isinstance(data, dict):
        raise ValueError('Ожидается JSON-объект')
    return data


def _positive_id(value):
    if (
        type(value) not in (int, str)
        or not str(value).isascii()
        or not str(value).isdecimal()
        or len(str(value)) > 19
        or not 0 < int(value) <= 2**63 - 1
    ):
        raise ValueError('Ожидается положительный идентификатор')
    return int(value)


def _json_error(error, status):
    return JsonResponse({'success': False, 'error': str(error)}, status=status)


def _parse_hints(items):
    if not isinstance(items, list) or len(items) > 20:
        raise ValueError('Ожидается список из не более 20 подсказок')
    result = []
    orders = set()
    hint_ids = set()
    for item in items:
        if not isinstance(item, dict):
            raise ValueError('Некорректная подсказка')
        order = _positive_id(item.get('order'))
        text = item.get('text')
        if order > 20 or order in orders:
            raise ValueError('Укажите уникальные номера подсказок от 1 до 20')
        if not isinstance(text, str) or not 0 < len(text.strip()) <= 1000:
            raise ValueError('Введите от 1 до 1000 символов в подсказке')
        if '\x00' in text:
            raise ValueError('Некорректный текст подсказки')
        text.encode('utf-8')
        hint_id = item.get('id')
        if hint_id is not None:
            hint_id = _positive_id(hint_id)
            if hint_id in hint_ids:
                raise ValueError('Подсказка указана дважды')
            hint_ids.add(hint_id)
        orders.add(order)
        result.append((order, text.strip(), hint_id))
    return result


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
        try:
            hints = None
            if 'hints_payload' in self.request.POST:
                hints = _parse_hints(
                    json.loads(self.request.POST['hints_payload'])
                )
        except (ValueError, RecursionError) as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        try:
            cipher = self.save_cipher(form, hints)
        except GameRuleError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)

        profile_url = reverse_lazy(
            'users:profile',
            kwargs={'username': self.request.user.username},
        )
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'success': True,
                    'cipher_id': cipher.id,
                    'redirect_url': profile_url,
                },
            )
        return redirect(profile_url)

    @transaction.atomic
    def save_cipher(self, form, hints):
        cipher = form.save(commit=False)
        cipher.author = self.request.user
        if self.cipher_id is None:
            cipher.cipher_type = 'community'
            cipher.save()
        elif form.changed_data:
            cipher.status = 'pending'
            cipher.save(
                update_fields=[*form.changed_data, 'status', 'updated_at'],
            )

        if hints is not None:
            save_cipher_hints(
                user=self.request.user, cipher_id=cipher.pk, hints=hints
            )
        return cipher

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    'success': False,
                    'errors': form.errors,
                },
            )

        return self.render_to_response(self.get_context_data(form=form))


class LibraryCommunityView(ListView):
    model = Cipher
    template_name = 'ciphers/library.html'
    context_object_name = 'ciphers'
    paginate_by = 9

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


class CipherAccessMixin:
    def get_cipher(self, request, cipher_id, *, lock=False):
        queryset = Cipher.objects.all()
        if not request.user.is_staff:
            queryset = queryset.filter(author=request.user)
        if lock:
            queryset = queryset.select_for_update(no_key=True)
        return get_object_or_404(queryset, pk=cipher_id)

    def redirect_back(self, request):
        referer = request.META.get('HTTP_REFERER')
        if url_has_allowed_host_and_scheme(
            referer,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(referer)
        return redirect('ciphers:library_community')


class HideCipherView(LoginRequiredMixin, CipherAccessMixin, View):
    @transaction.atomic
    def post(self, request, cipher_id):
        cipher = self.get_cipher(request, cipher_id, lock=True)

        if cipher.status == 'pending' or cipher.status == 'rejected':
            return HttpResponseForbidden(
                'Нельзя скрыть шифр на модерации или заблокированный шифр',
            )

        cipher.status = 'hidden'
        cipher.save(update_fields=['status', 'updated_at'])
        return self.redirect_back(request)


class OpenCipherView(LoginRequiredMixin, CipherAccessMixin, View):
    @transaction.atomic
    def post(self, request, cipher_id):
        cipher = self.get_cipher(request, cipher_id, lock=True)

        if cipher.status != 'hidden':
            return HttpResponseForbidden('Можно открыть только скрытые шифры')

        cipher.status = 'approved'
        cipher.save(update_fields=['status', 'updated_at'])
        return self.redirect_back(request)


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
        return get_object_or_404(
            visible_ciphers(self.request.user),
            pk=self.kwargs['cipher_id'],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cipher = self.object
        user = self.request.user
        hints = cipher.hints.all().order_by('order')
        purchased_hint_ids = set(
            PurchasedHint.objects.filter(
                user=user, hint__in=hints
            ).values_list('hint_id', flat=True)
        )
        purchased_hints = []
        available_hints = []
        for hint in hints:
            if hint.id in purchased_hint_ids or (
                user.is_staff and cipher.status == 'pending'
            ):
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
        context['qr_code'] = QR.objects.create_qr_for_cipher(
            cipher=cipher,
            request=self.request,
        )
        context['user_attempts'] = (
            SolutionLog.objects.user_solutions_for_cipher(
                self.request.user,
                cipher,
            )
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
        if cipher.attempt_limit is not None:
            last = context['last_attempt']
            context['left_attempt_cnt'] = max(
                0,
                cipher.attempt_limit - (last.attempts_used if last else 0),
            )

        context['solved_users_cnt'] = SolutionLog.objects.get_solved_users_cnt(
            self.object,
        )
        context['top_users'] = SolutionLog.objects.get_top_solvers(
            cipher,
        )
        context['has_limit'] = self.object.attempt_limit is not None
        if self.request.user.is_staff:
            context['complaints'] = Feedback.objects.received_for_cipher(
                cipher,
            )
            context['complaints_from_past'] = (
                Feedback.objects.answered_for_cipher(cipher)
            )

        return context

    def post(self, request, **kwargs):
        if 'moderation_action' in request.POST:
            try:
                moderate_cipher(
                    user=request.user,
                    cipher_id=kwargs['cipher_id'],
                    action=request.POST['moderation_action'],
                )
            except Cipher.DoesNotExist as exc:
                raise Http404 from exc
            except GameRuleError as exc:
                return HttpResponseBadRequest(str(exc))
            return redirect(request.path)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_hint_purchase(request)

        self.object = self.get_object()
        form = self.get_form()
        if not form.is_valid():
            return self.form_invalid(form)
        return self.form_valid(form)

    def handle_hint_purchase(self, request):
        try:
            hint_id = _positive_id(_read_json(request).get('hint_id'))
        except ValueError as exc:
            return _json_error(exc, 400)

        try:
            return JsonResponse(
                purchase_hint(
                    user=request.user,
                    cipher_id=self.kwargs['cipher_id'],
                    hint_id=hint_id,
                )
            )
        except (Cipher.DoesNotExist, CipherHelp.DoesNotExist):
            return _json_error('Подсказка не найдена', 404)

    def form_valid(self, form):
        try:
            submit_solution(
                user=self.request.user,
                cipher_id=self.object.pk,
                answer=form.cleaned_data['attempted_answer'],
            )
        except Cipher.DoesNotExist as exc:
            raise Http404 from exc
        except GameRuleError as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        return redirect(self.get_success_url())


class SaveCipherHintsView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = _read_json(request)
            cipher_id = _positive_id(data.get('cipher_id'))
            hints = _parse_hints(data.get('hints'))
        except ValueError as exc:
            return _json_error(exc, 400)
        try:
            save_cipher_hints(
                user=request.user, cipher_id=cipher_id, hints=hints
            )
        except Cipher.DoesNotExist:
            return _json_error('Шифр не найден', 404)
        except GameRuleError as exc:
            return _json_error(exc, 400)
        return JsonResponse({'success': True, 'hints_count': len(hints)})
