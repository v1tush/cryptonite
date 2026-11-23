from django.contrib.auth.views import (
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path, reverse_lazy

import users.views
from users.forms import PasswordChangeForm, SetPasswordForm

app_name = 'users'
urlpatterns = [
    path('signup/', users.views.SignupView.as_view(), name='signup'),
    path(
        'profile/<str:username>/',
        users.views.ProfileDetailView.as_view(),
        name='profile',
    ),
    path(
        'profile_edit/',
        users.views.ProfileEditView.as_view(),
        name='profile_edit',
    ),
    path(
        'login/',
        users.views.CustomLoginView.as_view(
            template_name='users/login.html',
        ),
        name='login',
    ),
    path(
        'logout/',
        LogoutView.as_view(
            template_name='users/logout.html',
        ),
        name='logout',
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(
            form_class=PasswordChangeForm,
            template_name='users/password_change.html',
            success_url=reverse_lazy('users:password_change_done'),
        ),
        name='password_change',
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_change_done',
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset.html',
            email_template_name='users/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            form_class=SetPasswordForm,
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
