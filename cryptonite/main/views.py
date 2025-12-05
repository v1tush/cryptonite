from django.http import HttpResponse


def home(request):
    return HttpResponse(
        '<a href="/users/signup/">регистрация (это здесь для удобства)</a>',
    )
