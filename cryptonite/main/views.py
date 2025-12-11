from django.views.generic import ListView

from ciphers.models import Cipher, CipherLike
from core.functions import get_user_ranking_position
from logs.models import SolutionLog


class HomeView(ListView):
    model = Cipher
    template_name = 'main/main.html'
    context_object_name = 'ciphers'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['likes_ciphers'] = list(
            map(
                lambda x: x.cipher,
                CipherLike.objects.filter(user=self.request.user),
            ),
        )
        ciphers = []
        for i in Cipher.objects.all():
            ciphers.append(SolutionLog.objects.get_solved_users_cnt(i))

        context['solved_users_cnt'] = ciphers
        context['solved_users_ciphers'] = list(
            map(
                lambda x: x.cipher,
                SolutionLog.objects.filter(
                    user=self.request.user,
                    correct=True,
                ).all(),
            ),
        )
        context['rank'] = get_user_ranking_position(self.request.user)
        return context
