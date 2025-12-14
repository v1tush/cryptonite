from django.views.generic import ListView

from ciphers.models import Cipher

# from ciphers.utils import get_today_cipher
# from core.functions import get_user_ranking_position


class HomeView(ListView):
    model = Cipher
    template_name = 'main/main.html'
    context_object_name = 'ciphers'

    def get_queryset(self):
        approved_and_popular = Cipher.objects.get_some_most_popular_ciphers(10)
        if not self.request.user.is_authenticated:
            return approved_and_popular

        return approved_and_popular.with_user_likes_and_solutions(
            self.request.user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('rank', None)
        return context
