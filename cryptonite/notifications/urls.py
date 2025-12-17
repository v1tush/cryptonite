from django.urls import path

import notifications.views

app_name = 'notifications'

urlpatterns = [
    path(
        'staff',
        notifications.views.StaffNotificationsView.as_view(),
        name='staff-notifications',
    ),
]
