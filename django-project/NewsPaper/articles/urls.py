from django.urls import path
from news.views import PostCreate, PostUpdate, PostDelete

urlpatterns = [
    path('create/', PostCreate.as_view(), name='article_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='article_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='article_delete'),
]
