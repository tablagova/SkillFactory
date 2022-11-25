from django.urls import path

from topics.views import *

urlpatterns = [
    path('topic/<int:pk>/', TopicView.as_view(), name='topic'),
    path('', TopicListView.as_view(), name='home'),
    path('topics/<int:cat_id>', TopicListByCategory.as_view(), name='topics_by_category'),
    path('reply/<int:pk>/', AddReply.as_view(), name='add_reply'),
    path('change_approve/<int:pk>', change_reply_approve, name='change_reply_approve'),
    path('add_topic/', AddTopic.as_view(), name='add_topic'),
    path('topic/<int:pk>/edit/', UpdateTopic.as_view(), name='update_topic'),
    path('topic/<int:pk>/delete/', DeleteTopic.as_view(), name='delete_topic'),
    path('private/', IndexView.as_view(), name='private_page'),
    path('replies/', TopicsFilterByAuthor.as_view(), name='replies'),
    path('alter_active_user/', AlterActiveUser.as_view(), name='alter_active_user'),
    path('login/', LoginUser.as_view(), name='user_login'),
    # path('logout/', logout_user, name='user_logout'),
    path('logout/', LogoutUser.as_view(), name='user_logout'),
    path('signup/', SignupUser.as_view(), name='user_signup'),
    path('code_verify/', LoginWithCode.as_view(), name='code_verify'),
]
