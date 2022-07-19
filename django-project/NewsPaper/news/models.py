from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

POST_TYPES = [
    ('article', 'статья'),
    ('news', 'новость'),
]


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = 0
        for post in Post.objects.filter(author=self):
            self.rating += post.rating * 3
        for comment in Comment.objects.filter(user=self.user):
            self.rating += comment.rating
        for comment in Comment.objects.all():
            if comment.post.author == self:
                self.rating += comment.rating
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.PROTECT, null=True)
    type = models.CharField(max_length=20, choices=POST_TYPES)
    create_date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    header = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:124] + '...'

    def __str__(self):
        return self.preview()

    def get_absolute_url(self):
        return reverse('post', kwargs={'id': self.id})


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        if self.rating > 0:
            self.rating -= 1
        self.save()

    def preview(self):
        return self.text[0:124] + '...'
