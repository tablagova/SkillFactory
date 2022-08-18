from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostSearch, add_subscription

urlpatterns = [
    path('', PostList.as_view(), name='post_list'),
    path('search/', PostSearch.as_view(), name='post_search'),
    path('<int:id>', PostDetail.as_view(), name='post'),
    path('create/', PostCreate.as_view(), name='news_create'),
    path('<int:pk>/edit/', PostUpdate.as_view(), name='news_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),
    path('subscribe/<int:cat_id>/', add_subscription, name='subscribe'),
]