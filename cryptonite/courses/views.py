import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from ciphers.models import Cipher
from courses.models import Course


class LibraryCoursesView(ListView):
    model = Course
    template_name = 'courses/courses.html'
    context_object_name = 'courses'


class CreateCourseView(LoginRequiredMixin, TemplateView):
    template_name = 'courses/create_course.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_ciphers'] = Cipher.objects.filter(
            author=self.request.user,
        ).approved().order_by('-created_at')
        context['form_data'] = {}
        context['errors'] = {}
        context['error_messages'] = []
        return context

    def post(self, request, *args, **kwargs):
        form_data = {
            'title': request.POST.get('title', '').strip(),
            'description': request.POST.get('description', '').strip(),
            'cipher_ids': request.POST.get('cipher_ids', '[]'),
        }
        errors = {}
        error_messages = []
        title = form_data['title']
        if not title:
            errors['title'] = ['Введите название курса']
        elif len(title) < 5:
            errors['title'] = ['Название должно содержать минимум 5 символов']
        elif len(title) > 200:
            errors['title'] = ['Название не должно превышать 200 символов']

        description = form_data['description']
        if not description:
            errors['description'] = ['Введите описание курса']
        elif len(description) < 100:
            errors['description'] = [
                'Описание должно содержать минимум 100 символов',
            ]

        cipher_ids = json.loads(form_data['cipher_ids'])
        if errors:
            return self.render_with_errors(request, form_data, errors)

        user_ciphers = Cipher.objects.filter(
            id__in=cipher_ids,
            author=request.user,
        ).approved()

        if user_ciphers.count() != len(cipher_ids):
            error_messages.append(
                'Некоторые шифры не найдены или вам не принадлежат',
            )
            return self.render_with_errors(
                request,
                form_data,
                {},
                error_messages,
            )

        with transaction.atomic():
            course = Course.objects.create(
                title=title,
                description=description,
                author=request.user,
            )

            for cipher_id in cipher_ids:
                cipher = Cipher.objects.get(id=cipher_id)
                cipher.cipher_type = 'course'
                cipher.course = course
                cipher.save()

        return redirect(reverse('courses:library_courses'))

    def render_with_errors(
        self,
        request,
        form_data,
        errors=None,
        error_messages=None,
    ):
        context = self.get_context_data()
        context.update(
            {
                'form_data': form_data,
                'errors': errors or {},
                'error_messages': error_messages or [],
                'user_ciphers': Cipher.objects.filter().order_by(
                    '-created_at',
                ),
            },
        )

        return render(request, self.template_name, context)


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    pk_url_kwarg = 'course_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ciphers'] = (
            Cipher.objects.filter(course=self.object)
            .approved()
            .with_user_likes_and_solutions(self.request.user)
        )

        return context
