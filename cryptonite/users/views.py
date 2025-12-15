import django.contrib.auth
import django.contrib.auth.mixins
from django.contrib.auth.views import LoginView
import django.contrib.messages
import django.shortcuts
import django.urls
import django.views.generic
import django.views.generic.edit

from ciphers.models import Cipher
from core.functions import get_user_ranking_position
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
        user_whose_profile = self.get_object()
        context = super().get_context_data(**kwargs)

        context[
            'created_ciphers'
        ] = user_whose_profile.ciphers.all().with_user_likes_and_solutions(
            self.request.user,
        )
        context['rank'] = get_user_ranking_position(user_whose_profile)
        context['solved_users_ciphers'] = (
            Cipher.objects.all()
            .get_all_user_solved_ciphers(user_whose_profile)
            .with_user_likes_and_solutions(
                self.request.user,
            )
        )
        context['solved_ciphers_count'] = len(context['solved_users_ciphers'])
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
        if form.has_changed():
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
