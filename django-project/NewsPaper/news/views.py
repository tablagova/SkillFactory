from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect

from .forms import PostForm
from .models import Post, Category
from .filters import PostFilter


# def notify_subscribers(sender, instance, created, **kwargs):
#     print(f'Новая публикация')
#     send_mail(
#         subject=f'Новая публикация',
#         message=f'Добавлена публикация',
#         from_email='t.a.blagova@yandex.ru',
#         recipient_list=['tablagova@gmail.com']
#     )
#
#
# post_save.connect(notify_subscribers, sender=Post)


class PostList(ListView):
    model = Post
    ordering = '-create_date'
    # queryset = Post.objects.filter(
    #     rating__gt=5
    # )
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'id'


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.path == reverse('article_create'):
            post.type = 'article'
        elif self.request.path == reverse('news_create'):
            post.type = 'news'
        else:
            raise ValidationError('Недопустимая операция')
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        form.save(commit=False)
        if ((self.request.path == reverse('article_update', kwargs={'pk': self.object.pk})
                and self.object.type == 'article')
                or
                (self.request.path == reverse('news_update', kwargs={'pk': self.object.pk})
                 and self.object.type == 'news')):
            return super().form_valid(form)
        else:
            raise ValidationError('Недопустимая операция')


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        if ((self.request.path == reverse('article_delete', kwargs={'pk': self.object.pk})
             and self.object.type == 'article') or
                (self.request.path == reverse('news_delete', kwargs={'pk': self.object.pk})
                 and self.object.type == 'news')):
            return super().form_valid(form)
        else:
            raise ValidationError('Недопустимая операция')


class PostSearch(PostList):
    template_name = 'posts_search.html'


def add_subscription(request, cat_id):
    category = Category.objects.get(id=cat_id)
    category.subscribers.add(request.user)
    return render(request, 'subscribe.html', {'category': category})
