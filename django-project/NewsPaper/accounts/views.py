from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView

from news.models import Author


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    Author.objects.create(user=user)
    authors = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors.user_set.add(user)
    return redirect('userpage')



