from django.urls import path

import main.views


app_name = 'main'
urlpatterns = [
    path('', main.views.HomeView.as_view(), name='main'),
]
