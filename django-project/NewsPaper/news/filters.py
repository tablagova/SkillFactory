from django_filters import FilterSet, ModelChoiceFilter, DateFilter, CharFilter
from django import forms

from .models import Post, Author


class PostFilter(FilterSet):

    header = CharFilter(
        lookup_expr='icontains',
        label='Название содержит',

    )

    author = ModelChoiceFilter(

        queryset=Author.objects.all(),
        label='Автор',
        empty_label='Все авторы',
    )

    create_date = DateFilter(
        lookup_expr='gt',
        widget=forms.widgets.DateInput(attrs={'type': 'date'}),
        label='Дата создания после'
    )

    class Meta:
        model = Post
        fields = {}
