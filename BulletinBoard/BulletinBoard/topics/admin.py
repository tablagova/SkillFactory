from django.contrib import admin
from .models import *


class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'category', 'title', 'simple_context', 'picture')
    list_display_links = ('id', 'title')


admin.site.register(ActiveUser)
admin.site.register(Category)
admin.site.register(Topic)
admin.site.register(Reply)
