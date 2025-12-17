from ciphers.models import Cipher


def count_pending_ciphers(request):
    if request.user.is_authenticated and request.user.is_staff:
        count = Cipher.objects.pending().count()
    else:
        count = 0

    return {'count_pending_ciphers': count}
