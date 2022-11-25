from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_managers, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse

from .models import Reply

SERVER_NAME = '127.0.0.1'
SERVER_PORT = '8000'


@receiver(post_save, sender=Reply)
def notify_reply(sender, instance, created, **kwargs):
    if created:
        subject = f'Поступил новый отклик на ваше объявление'
        message = f'Пользователь {instance.author.nickname} оставил отклик на ваше объявление' \
                  f' от {instance.create_date.strftime("%d %m %Y")} "{instance.topic.title}".'

        subscribers = [instance.topic.author.user.email]
        template = 'topics/notify_new_reply.html'

        full_url = ''.join(['http://', SERVER_NAME, ':', SERVER_PORT, reverse('private_page')])
        html_content = render_to_string(
            template,
            {
                'reply': instance,
                'full_url': full_url,
            }
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email='t.a.blagova@yandex.ru',
            to=subscribers,
        )

        msg.attach_alternative(html_content, "text/html")

        msg.send()
        print('Отправлено сообщение')
    else:
        if instance.approved:
            subject = f'Ваш отклик на объявление одобрен автором'
            message = f'Пользователь {instance.topic.author} одобрил ваш отклик на объявление ' \
                      f'от {instance.create_date.strftime("%d %m %Y")} "{instance.topic.title}'

            subscribers = [instance.author.user.email]
            template = 'topics/notify_approved_reply.html'

            full_url = ''.join(['http://', SERVER_NAME, ':', SERVER_PORT, instance.topic.get_absolute_url()])

            html_content = render_to_string(
                template,
                {
                    'reply': instance,
                    'full_url': full_url,
                }
            )

            msg = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email='t.a.blagova@yandex.ru',
                to=subscribers,
            )

            msg.attach_alternative(html_content, "text/html")

            msg.send()
            print('Отправлено сообщение')
