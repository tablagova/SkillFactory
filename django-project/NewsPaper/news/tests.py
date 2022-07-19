from django.test import TestCase
from .models import *
# Create your tests here.

post = Post.objects.get(pk=1)
print(post.get_type_display())
