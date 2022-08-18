from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post
from .params import SERVER_NAME, SERVER_PORT


@receiver(m2m_changed, sender=Post.category.through)
def notify_subscribers(sender, instance, action, **kwargs):
    categories = []
    subscribers = []

    if action == 'post_add':
        for cat in instance.category.all():
            cat_subscribers = cat.subscribers.all()
            if cat_subscribers:
                categories.append(cat.name)
                for user in cat_subscribers:
                    if user.email:
                        subscribers.append(user.email)
    subscribers = list(set(subscribers))

    full_url = ''.join(['http://', SERVER_NAME, ':', SERVER_PORT, instance.get_absolute_url()])

    html_content = render_to_string(
        'inform_new_post.html',
        {
            'post': instance,
            'full_url': full_url,
        }
    )

    msg = EmailMultiAlternatives(
        subject=f"Новая публикация в категориях: {', '.join(categories)}",
        body=f"{instance.preview()} ",
        from_email='t.a.blagova@yandex.ru',
        to=subscribers,
    )

    msg.attach_alternative(html_content, "text/html")

    msg.send()

