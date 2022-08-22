from datetime import datetime, timedelta, timezone

from celery import shared_task
import time

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from news.models import Post, Category
from news.params import SERVER_NAME, SERVER_PORT


@shared_task
def notify_subscribers(post_id):
    post = Post.objects.get(id=post_id)
    categories = []
    subscribers = []

    for cat in post.category.all():
        cat_subscribers = cat.subscribers.all()
        if cat_subscribers:
            categories.append(cat.name)
            for user in cat_subscribers:
                if user.email:
                    subscribers.append(user.email)
    subscribers = list(set(subscribers))

    full_url = ''.join(['http://', SERVER_NAME, ':', SERVER_PORT, post.get_absolute_url()])

    html_content = render_to_string(
        'inform_new_post.html',
        {
            'post': post,
            'full_url': full_url,
        }
    )

    msg = EmailMultiAlternatives(
        subject=f"Новая публикация в категориях: {', '.join(categories)}",
        body=f"{post.preview()} ",
        from_email='t.a.blagova@yandex.ru',
        to=subscribers,
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()

@shared_task
def weekly_mail():
    full_url = ''.join(['http://', SERVER_NAME, ':', SERVER_PORT])
    categories = Category.objects.all()
    for category in categories:
        # print(category.name)
        subscribers = []
        for user in category.subscribers.all():
            if user.email:
                subscribers.append(user.email)
        subscribers = list(set(subscribers))
        if subscribers:

            # print(subscribers)
            posts = Post.objects.filter(
                create_date__gt=datetime.now(tz=timezone.utc) - timedelta(weeks=1),
                category=category
            )

            html_content = render_to_string(
                'inform_posts_weekly.html',
                {
                    'posts': posts,
                    'full_url': full_url,
                    'category': category.name,
                }
            )

            msg = EmailMultiAlternatives(
                subject=f"Еженедельная рассылка по вашей подписке: {category.name}",
                body=f"Анонс статей, опубликованных в категории {category.name} за прошедшую неделю",
                from_email='t.a.blagova@yandex.ru',
                to=subscribers,
            )

            msg.attach_alternative(html_content, "text/html")

            msg.send()

