from django import forms
from django.core.exceptions import ValidationError

from .models import Post


class PostForm(forms.ModelForm):
    header = forms.CharField(min_length=20, label='Название')

    class Meta:
        model = Post
        fields = [
            'author',
            'category',
            'header',
            'text',
        ]

    def clean(self):
        cleaned_data = super().clean()
        header = cleaned_data.get("header")
        text = cleaned_data.get("text")
        if text == header:
            raise ValidationError(
                "Текст не должен быть идентичен заголовку."
            )

        return cleaned_data
