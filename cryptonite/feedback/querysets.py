from django.db import models


class FeedbackQuerySet(models.QuerySet):
    def all(self):
        return self.select_related('author', 'cipher')

    def received(self):
        return self.filter(status='received')

    def in_progress(self):
        return self.filter(status='in_progress')

    def answered(self):
        return self.filter(status='answered')

    def for_staff(self):
        return self.exclude(status='answered')

    def for_cipher(self, cipher):
        return self.filter(cipher=cipher)

    def for_cipher_id(self, cipher_id):
        return self.filter(cipher_id=cipher_id)

    def active_for_cipher(self, cipher):
        return self.for_cipher(cipher).exclude(status='answered')

    def received_for_cipher(self, cipher):
        return self.for_cipher(cipher).received()

    def in_progress_for_cipher(self, cipher):
        return self.for_cipher(cipher).in_progress()

    def answered_for_cipher(self, cipher):
        return self.for_cipher(cipher).answered()
