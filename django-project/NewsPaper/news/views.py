from datetime import datetime
from django.views.generic import ListView, DetailView
from django.shortcuts import render
from .models import Post


class PostList(ListView):
    model = Post
    ordering = '-create_date'
    # queryset = Post.objects.filter(
    #     rating__gt=5
    # )
    template_name = 'posts.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['next_post'] = None
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    pk_url_kwarg = 'id'
