from django.urls import path

import main.views


app_name = 'main'
urlpatterns = [
    path('', main.views.home, name='main'),
]
