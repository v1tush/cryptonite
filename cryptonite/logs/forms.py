from django import forms

from logs.models import SolutionLog


class SolutionLogForm(forms.ModelForm):
    attempted_answer = forms.CharField(
        label='',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Введите расшифрованный текст...',
                'id': 'solution-input',
            },
        ),
        error_messages={
            'required': 'Обязательное поле',
        },
        required=True,
    )

    class Meta:
        model = SolutionLog
        fields = ['attempted_answer']
