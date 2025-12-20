from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory, inlineformset_factory

from ciphers.models import Cipher, CipherHelp, CipherExample


class CipherWorkExampleField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            min_length=100,
            max_length=510,
            widget=forms.Textarea(
                attrs={
                    'placeholder': kwargs.get('placeholder'),
                    'class': 'form-textarea',
                    'id': kwargs.get('id'),
                    'rows': 5,
                },
            ),
            error_messages={
                'required': 'Обязательное поле',
                'min_length': 'Описание должно быть не менее 100 символа',
                'max_length': 'Описание не может превышать 510 символов',
            },
            required=True,
            label=kwargs.get('label'),
        )


class CipherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        self.create_flag = kwargs.pop('create_flag', True)

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

    description = CipherWorkExampleField(
        label='Описание шифра (видно всем)',
        placeholder='Введите описание шифра',
        id='cipher-description',
    )
    description_for_moderator = CipherWorkExampleField(
        label='Описание работы алгоритма',
        placeholder='Введите описание работы алгоритма',
        id='cipher-description-for-moderator',
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
        widget=forms.NumberInput(
            attrs={
                'min': 1,
                'max': 15,
                'placeholder': 'Введите количество попыток'
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
            'description_for_moderator',
            'difficulty',
            'attempt_limit',
        )

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

        return answer_phrase

    def clean_attempt_limit(self):
        attempt_limit = self.cleaned_data.get('attempt_limit')
        if attempt_limit is not None and attempt_limit < 1:
            raise ValidationError('Количество попыток должно быть больше 0')

        return attempt_limit

    def save(self, commit=True):
        cipher = super().save(commit=False)
        try:
            cipher.author = self.author
        except ValidationError:
            return None

        if commit:
            cipher.save()

        return cipher


class CipherHelpForm(forms.ModelForm):
    class Meta:
        model = CipherHelp
        fields = ('text',)


CipherHelpFormSet = modelformset_factory(
    CipherHelp,
    fields=('text', 'order'),
    extra=0,
    max_num=5,
    validate_max=True,
    can_delete=True,
)


CipherExampleFormSet = inlineformset_factory(
    Cipher,
    CipherExample,
    fields=('encrypted_phrase', 'answer_phrase'),
    extra=3,
    min_num=3,
    max_num=3,
    validate_min=True,
    validate_max=True,
    can_delete=False,
)