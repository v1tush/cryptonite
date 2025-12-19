from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

from ciphers.models import Cipher, CipherHelp


class CipherWorkExampleField(forms.CharField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            min_length=1,
            max_length=100,
            widget=forms.Textarea(
                attrs={
                    'placeholder': kwargs.get('placeholder'),
                    'class': 'form-textarea',
                    'rows': 5,
                },
            ),
            error_messages={
                'required': 'Обязательное поле',
                'min_length': 'Описание должно быть не менее 1 символа',
                'max_length': 'Описание не может превышать 100 символов',
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

    description = forms.CharField(
        label='Описание шифра (видно всем)',
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

    description_for_admin = forms.CharField(
        label='Описание алгоритма решения шифра (видно только модератору)',
        min_length=70,
        max_length=500,
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Введите описание алгоритма решения шифра',
                'class': 'form-textarea',
                'id': 'cipher-description',
                'rows': 5,
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
            'min_length': 'Описание должно быть не менее 10 символов',
            'max_length': 'Описание не может превышать 500 символов',
        },
        required=True,
    )

    first_example_encrypted_phrase = CipherWorkExampleField(
        label='Пример зашифрованной фразы 1 (Видно только модератору)',
        placeholder='Введите пример зашифрованной фразы',
    )
    first_example_answer_phrase = CipherWorkExampleField(
        label='Ответ примера 1',
        placeholder='Введите ответ для примера',
    )
    second_example_encrypted_phrase = CipherWorkExampleField(
        label='Пример зашифрованной фразы 2 (Видно только модератору)',
        placeholder='Введите пример зашифрованной фразы',
    )
    second_example_answer_phrase = CipherWorkExampleField(
        label='Ответ примера 2',
        placeholder = 'Введите ответ для примера',
    )
    third_example_encrypted_phrase = CipherWorkExampleField(
        label='Пример зашифрованной фразы 3 (Видно только модератору)',
        placeholder='Введите пример зашифрованной фразы',
    )
    third_example_answer_phrase = CipherWorkExampleField(
        label='Ответ примера 3',
        placeholder = 'Введите ответ для примера',
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
    can_delete=True,
)
