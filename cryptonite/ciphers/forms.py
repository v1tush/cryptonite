from django import forms
from django.forms import modelformset_factory

from ciphers.models import Cipher, CipherHelp


class CipherForm(forms.ModelForm):
    class Meta:
        model = Cipher
        fields = (
            'title',
            'encrypted_phrase',
            'answer_phrase',
            'description',
            'difficulty',
            'attempt_limit',
            'is_published',
        )


class CipherHelpForm(forms.ModelForm):
    class Meta:
        model = CipherHelp
        fields = ('text',)


CipherHelpFormSet = modelformset_factory(
    CipherHelp,
    fields=('text', 'order'),
    extra=0,
    can_delete=True,
)
