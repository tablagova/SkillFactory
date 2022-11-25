import os

from django.conf.global_settings import STATIC_ROOT
from django.contrib.auth.models import User
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse

from BulletinBoard.settings import BASE_DIR


class ActiveUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/%d')

    def __str__(self):
        return self.nickname


class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('topics_by_category', kwargs={'cat_id': self.pk})


class Topic(models.Model):
    author = models.ForeignKey(ActiveUser, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True,
                                     external_plugin_resources=[(
                                         'youtube',
                                         '/static/ckeditor/ckeditor/plugins/youtube/',
                                         'plugin.js',
                                     )
                                     ])
    simple_context = models.TextField(default='')
    # picture = models.ImageField(upload_to='pictures/%Y/%m/%d')

    def __str__(self):
        return f'{self.author.nickname} | {self.create_date.strftime("%d-%m-%Y")} | {self.title[:25]}...'

    def approved_replies(self):
        return self.reply_set.filter(approved=True)

    def get_absolute_url(self):
        return reverse('topic', kwargs={'pk': self.pk})


class Reply(models.Model):
    author = models.ForeignKey(ActiveUser, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author.nickname} | {self.create_date.strftime("%d-%m-%Y")} | {self.text[:25]}...'


class OneTimeCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=10)

