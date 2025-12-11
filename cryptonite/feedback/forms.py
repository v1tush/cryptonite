from django import forms

from feedback.models import Feedback


class FeedbackForm(forms.ModelForm):
    text = forms.CharField(
        label='Жалоба',
        widget=forms.Textarea(
            attrs={
                'placeholder': 'Напишите причину обращения (необязательно)',
                'class': 'form-textarea sub-text',
                'id': 'cipher-description',
                'rows': 7,
            },
        ),
        required=False,
    )

    class Meta:
        model = Feedback
        fields = ['text']
