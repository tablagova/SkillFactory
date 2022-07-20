import re
from django import template

register = template.Library()

RESTRICTED = [
    'пациент',
    'медицин',
    'физкультур',
    'эволюц',
    'исследов',
    'лицензи',
    'един',
]


@register.filter()
def currency(value):
    return f'{value}'


@register.filter()
def verbose_type_name(post):
    return post.get_type_display()


@register.filter()
def censor(text):
    word_list = re.split(r'\W+', text)
    for word in word_list:
        for pattern in RESTRICTED:
            if re.search(pattern, word.lower()):
                repl = word[0] + '*' * (len(word) - 1)
                text = re.sub(word, repl, text, count=0)
    return text
