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
    path(
        '<int:cipher_id>/hide/',
        ciphers.views.HideCipherView.as_view(),
        name='hide_cipher',
    ),
    path(
        '<int:cipher_id>/like/',
        ciphers.views.LikeCipherView.as_view(),
        name='like_cipher',
    ),
    path(
        '<int:cipher_id>/open/',
        ciphers.views.OpenCipherView.as_view(),
        name='open_cipher',
    ),
    path(
        '<int:cipher_id>/solve/',
        ciphers.views.SolveCipherView.as_view(),
        name='solve_cipher',
    ),
    path(
        'library_courses/',
        ciphers.views.LibraryCoursesView.as_view(),
        name='library_courses',
    ),
    path(
        'library_community/',
        ciphers.views.LibraryCommunityView.as_view(),
        name='library_community',
    ),
]
