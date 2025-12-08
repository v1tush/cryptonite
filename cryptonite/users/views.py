import django.contrib.auth
import django.contrib.auth.mixins
import django.contrib.messages
import django.shortcuts
import django.urls
import django.views.generic
import django.views.generic.edit

import users.forms


# ! Форма регистрации пользователя
class SignupView(django.views.generic.FormView):
    template_name = 'users/signup.html'
    form_class = users.forms.UserCreationForm

    def form_valid(self, form):
        user = form.save()
        django.contrib.auth.login(self.request, user)

        return django.shortcuts.redirect(
            'users:profile',
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form),
        )

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return django.shortcuts.redirect(
                'users:profile',
            )

        return super().dispatch(request, *args, **kwargs)


class ProfileView(
    django.contrib.auth.mixins.LoginRequiredMixin,
    django.views.generic.edit.UpdateView,
    django.views.generic.FormView,
):
    template_name = 'users/profile.html'
    form_class = users.forms.ProfileChangeForm
    login_url = django.urls.reverse_lazy('users:login')
    # ! Прошу фронтендера перепроверить корректность путей

    def get_initial(self):
        initial = super().get_initial()

        initial.update(
            'username', self.request.user.username,
            'first_name', self.request.user.first_name,
            'last_name', self.request.user.last_name,
            'email', self.request.user.email,
            'avatar', self.request.user.avatar,
        )

        return initial

    def form_valid(self, form):
        django.contrib.messages.success(
            self.request,
            'Ваш профиль успешно обновлен.',
        )

        return super().form_valid(form)
