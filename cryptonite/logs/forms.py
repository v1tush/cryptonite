from django import forms

from logs.models import SolutionLog


class SolutionLogForm(forms.ModelForm):
    class Meta:
        model = SolutionLog
        fields = ['attempted_answer']
