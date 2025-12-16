from django.db import models

from feedback.querysets import FeedbackQuerySet


class FeedbackManager(models.Manager):
    def get_queryset(self):
        return FeedbackQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().all()

    def received(self):
        return self.get_queryset().received()

    def in_progress(self):
        return self.get_queryset().in_progress()

    def answered(self):
        return self.get_queryset().answered()

    def for_staff(self):
        return self.get_queryset().for_staff()

    # ===== по шифру =====
    def for_cipher(self, cipher):
        return self.get_queryset().for_cipher(cipher)

    def for_cipher_id(self, cipher_id):
        return self.get_queryset().for_cipher_id(cipher_id)

    # ===== комбинированные =====
    def active_for_cipher(self, cipher):
        return self.get_queryset().active_for_cipher(cipher)

    def received_for_cipher(self, cipher):
        return self.get_queryset().received_for_cipher(cipher)

    def in_progress_for_cipher(self, cipher):
        return self.get_queryset().in_progress_for_cipher(cipher)

    def answered_for_cipher(self, cipher):
        return self.get_queryset().answered_for_cipher(cipher)
