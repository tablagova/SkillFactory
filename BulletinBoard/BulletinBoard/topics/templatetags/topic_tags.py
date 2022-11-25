from django import template
from topics.models import Category, ActiveUser

register = template.Library()


@register.simple_tag()
def get_categories():
    return Category.objects.all()


@register.simple_tag()
def get_nickname(user):
    nickname = ActiveUser.objects.get(user=user).nickname
    return nickname

@register.simple_tag()
def get_avatar(user):
    avatar = ActiveUser.objects.get(user=user).avatar.url
    return avatar