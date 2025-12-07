from django.urls import path

import ciphers.views

app_name = 'ciphers'

urlpatterns = [
    path(
        'create/',
        ciphers.views.CreateEditCipher.as_view(),
        name='create_cipher',
    ),
    path(
        'edit/<int:cipher_id>/',
        ciphers.views.CreateEditCipher.as_view(),
        name='edit_cipher',
    ),
]
