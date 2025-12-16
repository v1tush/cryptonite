from django.urls import path

import notifications.views

app_name = 'notifications'

urlpatterns = [
    path(
        '/stuff',
        notifications.views.StaffNotificationsView.as_view(),
        name='notifications',
    )
]
