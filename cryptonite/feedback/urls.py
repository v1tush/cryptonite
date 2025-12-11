from django.urls import path

import feedback.views


app_name = 'feedback'
urlpatterns = [
    path(
        '<int:cipher_id>/',
        feedback.views.FeedbackView.as_view(),
        name='feedback',
    ),
]
