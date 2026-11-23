from django.urls import path

import courses.views

app_name = 'courses'

urlpatterns = [
    path(
        'library_courses/',
        courses.views.LibraryCoursesView.as_view(),
        name='library_courses',
    ),
    path(
        'create_course/',
        courses.views.CreateCourseView.as_view(),
        name='create_course',
    ),
    path(
        '<int:course_id>/',
        courses.views.CourseDetailView.as_view(),
        name='detail',
    ),
]
