import random
import string

from allauth.account.views import LoginView, LogoutView, SignupView
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View

from .forms import ReplyForm, TopicForm, ActiveUserForm, LoginUserForm, SignupUserForm
from .management.commands.tasks import send_email
from .models import *

from django.views.generic import DetailView, ListView, CreateView, TemplateView, UpdateView, DeleteView


def get_one_time_code():
    symbols = string.ascii_letters + string.digits
    code = ''.join(random.choice(symbols) for _ in range(10))
    return code


def send_code(email, code):
    subject = f'Проверочный код'
    message = f'Код для входа {code}'
    html_content = render_to_string(
        'topics/inform_simple.html',
        {
            'title': f'Код для входа {code}',
            'text': 'Код для входа действует только один раз',
        }
    )
    send_email(html_content, subject, message, [email])


def change_reply_approve(request, pk):
    reply = Reply.objects.get(pk=pk)
    reply.approved = False if reply.approved else True
    reply.save()
    return redirect('replies')


class TopicView(DetailView):
    model = Topic
    template_name = 'topics/topic.html'


class TopicListView(ListView):
    model = Topic
    ordering = '-create_date'
    template_name = 'topics/topic_list.html'
    paginate_by = 5


class TopicListByCategory(ListView):
    model = Topic
    ordering = '-create_date'
    template_name = 'topics/topic_list.html'
    paginate_by = 1

    def get_queryset(self):
        return Topic.objects.filter(category_id=self.kwargs['cat_id'])


class TopicsFilterByAuthor(LoginRequiredMixin, ListView):
    model = Reply

    template_name = 'topics/replies.html'
    context_object_name = 'replies'

    def get_queryset(self):
        topics = Topic.objects.filter(author__user_id=self.request.user).values('id')
        return Reply.objects.filter(topic_id__in=topics).order_by('-create_date')


class AddReply(LoginRequiredMixin, View):

    def post(self, request, pk):
        form = ReplyForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.topic_id = pk
            if request.user.is_authenticated:
                form.author = ActiveUser.objects.get(user=request.user)
            else:
                raise PermissionError
            form.save()
        return redirect(reverse('topic', kwargs={'pk': pk}))


class AlterActiveUser(LoginRequiredMixin, View):

    def post(self, request):
        form = ActiveUserForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                active_user = ActiveUser.objects.get(user_id=User.objects.get(username=request.user).id)
                active_user.nickname = request.POST['nickname']
                active_user.avatar = request.FILES['avatar']
                active_user.save()
            except:
                form = form.save(commit=False)
                form.user = request.user
                form.save()
        return redirect(reverse('home'))


class AddTopic(LoginRequiredMixin, CreateView):
    form_class = TopicForm
    model = Topic
    template_name = 'topics/topic_add.html'

    def post(self, request, *args, **kwargs):
        topic = TopicForm(request.POST, request.FILES)
        if topic.is_valid():
            topic = topic.save(commit=False)
            topic.author = ActiveUser.objects.get(user_id=User.objects.get(username=request.user).id)
            topic.save()
        return redirect('home')


class UpdateTopic(LoginRequiredMixin, UpdateView):
    form_class = TopicForm
    model = Topic
    template_name = 'topics/topic_edit.html'

    def form_valid(self, form):
        print(f'{self.request.user}')
        print(f'{type(self.request.user)}')

        form.save(commit=False)
        if self.request.user == self.object.author.user:
            return super().form_valid(form)
        else:
            raise ValidationError('Недопустимая операция')


class DeleteTopic(LoginRequiredMixin, DeleteView):
    model = Topic
    template_name = 'topics/topic_delete.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if self.request.user == self.object.author.user:
            return super().form_valid(form)
        else:
            raise ValidationError('Недопустимая операция')


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'topics/private_page.html'


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'topics/login.html'

    def form_valid(self, form):
        user = form.cleaned_data
        email = user['login']
        password = user['password']
        user = authenticate(email=email, password=password)
        if user is not None:
            symbols = string.ascii_letters + string.digits
            code = ''.join(random.choice(symbols) for _ in range(10))
            OneTimeCode.objects.create(code=code, user=user)
            send_code(email, code)

            return render(self.request, 'topics/login_with_code.html',
                          context={'email': email, 'password': password}
                          )
        else:
            return HttpResponse('Bad credentials')


class LogoutUser(LogoutView):
    template_name = 'topics/logout.html'


class SignupUser(SignupView):
    form_class = SignupUserForm
    template_name = 'topics/signup.html'

    def form_valid(self, form):
        user = form.save(self.request)
        nickname = self.request.POST['nickname']
        ActiveUser.objects.create(user=user, nickname=nickname, avatar=self.request.FILES['avatar'])
        email = self.request.POST['email']
        password = self.request.POST['password1']
        user = authenticate(self.request, email=email, password=password)
        if user is not None:
            code = get_one_time_code()
            OneTimeCode.objects.create(code=code, user=user)
            send_code(email, code)

            return render(self.request, 'topics/login_with_code.html', context={'email': email, 'password': password})
        else:
            return HttpResponse('Bad user')


class LoginWithCode(TemplateView):

    template_name = 'topics/login_with_code.html'

    def post(self, request):
        email = request.POST['email']
        code = request.POST['code']
        try:
            OneTimeCode.objects.get(code=code, user__email=email)
            user = authenticate(email=email, password=request.POST['password'])
            login(request, user)
            OneTimeCode.objects.filter(user__email=email).delete()
            return redirect('home')
        except:
            return HttpResponse('Код недействителен')

