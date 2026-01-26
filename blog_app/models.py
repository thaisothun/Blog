from django.db import models 
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.signals import post_save

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.name}' 

class Post(models.Model):
    topics = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    title = models.CharField(max_length=200)
    topic_status = models.CharField(choices=[('normal','Normal'),('vip','VIP')], default='normal')
    slug = models.SlugField(max_length=200, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    image1 = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    status = models.IntegerField(choices=[(0,'draft'),(1,'Published')],default=0)
    views = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='post_like', blank=True)
    
    class Meta:
        ordering = ['-created_on']
    def __str__(self):
        return self.title
    
    def topicsCount():     
        results = Category.objects.annotate(post_count=Count('category')).order_by('name')
        return results
    
class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='userprofile')
    short_message = models.CharField(max_length=100, blank=True, null=True)
    image_profile = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    gender = models.CharField(choices=[('Male','Male'),('Femal','Femal')])
    date_of_brith = models.DateField(blank=True, null=True)
    membership = models.CharField(choices=[('normal','Normal'),('vip','VIP')], default='normal')
    phone_number = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return f'{self.user}'

def createProfile(sender, instance, created, **kwargs):
    if created:
        print(instance)
        profile = UserProfile.objects.create(user=instance)
        profile.save()

post_save.connect(createProfile, sender=User)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}, {self.post}'
    