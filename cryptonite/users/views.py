import django.contrib.auth
import django.contrib.auth.mixins
from django.contrib.auth.views import LoginView
import django.contrib.messages
import django.shortcuts
import django.urls
import django.views.generic
import django.views.generic.edit

from ciphers.models import Cipher, CipherLike
from core.functions import get_user_ranking_position
from logs.models import SolutionLog
import users.forms
from users.models import CustomUser


class SignupView(django.views.generic.FormView):
    template_name = 'users/signup.html'
    form_class = users.forms.UserCreationForm

    def form_valid(self, form):
        user = form.save()
        django.contrib.auth.login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return django.urls.reverse_lazy(
            'users:profile',
            kwargs={'username': self.request.user.username},
        )

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return django.shortcuts.redirect(self.get_success_url())

        return super().dispatch(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'

    def get_success_url(self):
        return django.urls.reverse_lazy(
            'users:profile',
            kwargs={'username': self.request.user.username},
        )


class ProfileDetailView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.DetailView,
):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'

    def get_object(self, queryset=None):
        username = self.kwargs.get('username')
        return django.shortcuts.get_object_or_404(
            CustomUser,
            username=username,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ciphers'] = self.get_object().ciphers.with_user_likes(
            self.request.user,
        )
        context['likes_ciphers'] = list(
            map(
                lambda x: x.cipher,
                CipherLike.objects.filter(user=self.request.user),
            ),
        )
        context['rank'] = get_user_ranking_position(self.get_object())
        ciphers = []
        for i in Cipher.objects.filter(author=self.get_object()).all():
            ciphers.append(SolutionLog.objects.get_solved_users_cnt(i))

        context['solved_users_cnt'] = ciphers
        context['solved_users_ciphers'] = list(
            map(
                lambda x: x.cipher,
                SolutionLog.objects.filter(
                    user=self.request.user,
                    correct=True,
                ).all(),
            ),
        )
        return context


class ProfileEditView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.edit.UpdateView,
):
    model = CustomUser
    template_name = 'users/profile_edit.html'
    form_class = users.forms.ProfileChangeForm
    login_url = django.urls.reverse_lazy('users:login')
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        django.contrib.messages.success(
            self.request,
            'Ваш профиль успешно обновлен.',
        )

        return super().form_valid(form)

    def get_success_url(self):
        return django.urls.reverse_lazy(
            'users:profile',
            kwargs={'username': self.request.user.username},
        )
