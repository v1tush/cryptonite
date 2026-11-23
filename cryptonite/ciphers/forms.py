from django import forms
from django.core.exceptions import ValidationError

from ciphers.models import Cipher
from ciphers.services import normalize_answer


class CipherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.initial['difficulty'] = str(self.instance.difficulty)

        for field in self.visible_fields():
            field.field.widget.attrs['class'] = 'form-input'

    title = forms.CharField(
        label='Название шифра',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите название шифра',
                'id': 'cipher-name',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    encrypted_phrase = forms.CharField(
        label='Зашифрованная фраза',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите зашифрованное слово',
                'id': 'encrypted-phrase',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    answer_phrase = forms.CharField(
        label='Правильный ответ',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите расшифрованное слово',
                'id': 'answer-phrase',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    description = forms.CharField(
        label='Описание алгоритма',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Введите описание шифра',
                'class': 'form-textarea',
                'id': 'cipher-description',
                'rows': 5,
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    difficulty = forms.ChoiceField(
        label='Сложность шифра',
        choices=Cipher.DIFFICULTY_CHOICES,
        widget=forms.RadioSelect(
            attrs={'class': 'hidden-radio'},
        ),
        initial=2,
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    attempt_limit = forms.IntegerField(
        label='Количество попыток',
        min_value=1,
        max_value=15,
        widget=forms.NumberInput(
            attrs={
                'min': 1,
                'max': 15,
                'placeholder': 'Введите количество попыток '
                '(оставьте это поле пустым, '
                'если количество попыток бесконечно)',
            },
        ),
        required=False,
    )

    class Meta:
        model = Cipher
        fields = (
            'title',
            'encrypted_phrase',
            'answer_phrase',
            'description',
            'difficulty',
            'attempt_limit',
        )

    def clean_description(self):
        description = self.cleaned_data.get('description', '')
        if len(description) < 100:
            raise ValidationError(
                'Описание должно содержать не менее 100 символов',
            )

        if len(description) > 510:
            raise ValidationError('Описание не должно превышать 510 символов')

        return description

    def clean_encrypted_phrase(self):
        encrypted_phrase = self.cleaned_data.get('encrypted_phrase', '')
        if len(encrypted_phrase) > 100:
            raise ValidationError(
                'Зашифрованная фраза не должна превышать 100 символов',
            )

        return encrypted_phrase

    def clean_answer_phrase(self):
        answer_phrase = self.cleaned_data.get('answer_phrase', '')
        if len(answer_phrase) > 100:
            raise ValidationError('Ответ не должен превышать 100 символов')

        if not normalize_answer(answer_phrase):
            raise ValidationError('Введите ответ, содержащий буквы или цифры')
        return answer_phrase
