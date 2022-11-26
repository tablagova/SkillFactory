from datetime import datetime, timedelta, timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from topics.models import Topic, Category, ActiveUser

SERVER_NAME = '127.0.0.1'
SERVER_PORT = '8000'


def send_email(html_content, subject, body, to):

    msg = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email='t.a.blagova@yandex.ru',
        to=to,
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()


def weekly_mail():
    full_url = ''.join(['http://', SERVER_NAME, ':', SERVER_PORT])
    subscribers = []
    new_topics = Topic.objects.filter(create_date__gt=datetime.now(tz=timezone.utc) - timedelta(weeks=1))
    for user in ActiveUser.objects.all():
        if user.user.email:
            subscribers.append(user.user.email)
        subscribers = list(set(subscribers))

    html_content = render_to_string(
        'topics/inform_weekly.html',
        {
            'topics': new_topics,
            'full_url': full_url,
        }
    )
    email_subject = f"Еженедельная рассылка о новых объявлениях"
    email_body = f"Анонс объявлений, опубликованных за прошедшую неделю"

    send_email(html_content, email_subject, email_body, subscribers)
