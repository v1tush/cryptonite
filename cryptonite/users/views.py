import django.contrib.auth
import django.shortcuts
import django.urls
import django.views.generic

import users.forms


# ! Форма регистрации пользователя
class SignupView(django.views.generic.FormView):
    template_name = 'users/signup.html'
    form_class = users.forms.UserCreationForm

    def form_valid(self, form):
        user = form.save()
        django.contrib.auth.login(self.request, user)

        return django.shortcuts.redirect(
            '',  # ! TODO: Фротендеру добавть страницу для редиректа
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form),
        )

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return django.shortcuts.redirect(
                '',  # ! TODO: Фротендеру добавть страницу для редиректа
            )

        return super().dispatch(request, *args, **kwargs)
