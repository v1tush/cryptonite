from django.urls import path
from django.views.generic import TemplateView


app_name = 'core'

urlpatterns = [
    path(
        'privacy-policy/',
        TemplateView.as_view(template_name='core/privacy_policy.html'),
        name='privacy_policy',
    ),
]
