from allauth.account.forms import LoginForm, SignupForm, ChangePasswordForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Reply, Topic, ActiveUser


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ('text',)


class ActiveUserForm(forms.ModelForm):
    class Meta:
        model = ActiveUser
        fields = ('nickname', 'avatar')


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = (
            'category',
            'title',
            'simple_context',
            'content',
        )


class LoginUserForm(LoginForm):

    class Meta:
        model = User
        fields = ('email', 'password1')


class SignupUserForm(SignupForm):
    email = forms.EmailField(label='e-mail', widget=forms.TextInput())
    password1 = forms.CharField(label='Введите пароль', widget=forms.PasswordInput(attrs={'title': 'Введите пароль'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput())
    nickname = forms.CharField(label='Псевдоним', widget=forms.TextInput())
    avatar = forms.FileField(label='Аватар')

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        nickname = cleaned_data.get('nickname')
        if ActiveUser.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError(
                "Пользователь с таким псевдонимом уже зарегистрирован, выберите другой"
            )

        return cleaned_data


