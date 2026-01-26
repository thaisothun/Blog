from django.shortcuts import render, redirect, get_object_or_404
from .form import registationForm, loginForm, commentForm, profileUpdateForm1, profileUpdateForm2, CustomPasswordChangeForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post, Comment, UserProfile, User
from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count
from datetime import date 
import calendar
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.
    
def index(request):
    return redirect('home')

def home(request):
    posts = Post.objects.all()
    most_views = Post.objects.all().order_by('-views')[0:5]
    six_months = date.today() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
    topics = Post.topicsCount()
    
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    
    page = Paginator(posts,5)
    page_numb = request.GET.get('page',1)
    page_obj = page.page(page_numb)
    if request.user.is_authenticated:
        user = User.objects.get(username= request.user)
        profile = user.userprofile    
    else:
        profile= None
    context = {'posts':posts, 'converted_list':converted_list,'topics':topics,'page_obj':page_obj,'most_views':most_views, 'profile':profile}
    return render(request, 'blog_app\home.html', context )

def register(request):
    form=registationForm()
    if request.method=="POST":
        first_name = str(request.POST.get('first_name')).upper()
        last_name = str(request.POST.get('last_name')).upper()
        updatedata = request.POST.copy()
        updatedata['first_name'] = first_name
        updatedata['last_name'] = last_name
        form = registationForm(updatedata)
        if form.is_valid():                          
            form.save()
            return redirect('login')
    context = {'form':form} 
    return render (request,'blog_app/register.html', context)

def login(request):
    form=loginForm()
    error = ''
    user = ''
    if request.method=="POST":
        form = loginForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request,user)
            
            return redirect('home')
        if user is None and username is not None:
            error = "Username and password not matched"
            
    context = {'form':form,'error': error, 'user' : user}
    return render (request,'blog_app\login.html',context)

def logOutPost(request,pk):
    auth_logout(request)
    return redirect(reverse('detail-content', kwargs={'pk':pk}))
    
def logOutHome(request):
    auth_logout(request)
    return redirect('home')

def detailContent(request,pk):
    comment_form = commentForm()
    post = get_object_or_404(Post,pk=pk)
    
    if post.topic_status == 'vip':
        if request.user.is_authenticated:
            user = User.objects.get(username= request.user)
            if user.userprofile.membership == 'normal':
                
                return redirect('membership')
        if  request.user.is_authenticated == False:
            return redirect('membership')    
    
    post.views = post.views+1
    post.save()
    recent_post = Post.objects.order_by('-created_on')[:3]
    comments = post.comments.all().order_by('-create_date')
    
    total_likes = post.likes.count()
    user_like_post = False
    
    if request.user.is_authenticated:
        user_like_post = post.likes.filter(id=request.user.id).exists()
        user = User.objects.get(username= request.user)
        profile = user.userprofile
        
    else:
        profile= None
        
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')

    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    topics = Post.topicsCount()
    most_views = Post.objects.all().order_by('-views')[0:5]
    context = {'post':post,'recent_post':recent_post,'total_likes':total_likes,'user_like_post': user_like_post, 'comment_form':comment_form,'comments':comments, 'converted_list':converted_list, 'topics':topics, 'most_views':most_views, 'profile':profile}
    return render(request,'blog_app\detail_content.html',context)

def likePost(request,pk):
    post = get_object_or_404(Post,pk=pk)
    user = request.user
    if request.user.is_authenticated:
        user_like_post = post.likes.filter(id=request.user.id).exists()
        if user_like_post == False:
            post.likes.add(user)
            return redirect(reverse('detail-content', kwargs={'pk':pk}))
        else:
            post.likes.remove(user)
            return redirect(reverse('detail-content', kwargs={'pk':pk}))
    else:
        
        messages.info(request, 'You need to login to perform the action')
        return redirect(reverse('detail-content', kwargs={'pk':pk})) 
       
def commentPost(request,pk):
    if request.user.is_authenticated:
        comment = request.POST.get('content')
        id = Post(pk)
        new_comment = Comment(content=comment, user = request.user, post= id)
        new_comment.save()
        return redirect(reverse('detail-content', kwargs={'pk':pk})) 
    else:
        messages.info(request,'You need to login to perform the action')
        return redirect(reverse('detail-content', kwargs={'pk':pk}))

def searchPost(request):
    search1 = request.GET.get('search')
    
    if search1 == None and request.user.is_authenticated:
        search1 = request.session.get('temporary_data')
        
        search_results = Post.objects.filter(title__icontains=search1)
        current_user = get_object_or_404(User,username=request.user)
        profile = current_user.userprofile
        print('b')        
    
    else:    
        search_results = Post.objects.filter(title__icontains=search1)
        request.session['temporary_data'] = request.GET['search']   
        profile= None
        print('a')       
    
    if request.user.is_authenticated:
        current_user = get_object_or_404(User,username=request.user)
        profile = current_user.userprofile

    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
   
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    topics = Post.topicsCount()
    page = Paginator(search_results,5)
    page_numb = request.GET.get('page',1)
    page_obj = page.page(page_numb)
    most_views = Post.objects.all().order_by('-views')[0:5]
    context = {'search_results':search_results,'search':search1,'converted_list':converted_list,'topics':topics,'page_obj':page_obj,'most_views':most_views,'profile':profile}
    return render(request, 'blog_app\search_result.html', context)

def archivePost(request, month, year):
    monthfull = calendar.month_name[int(month)]
    if request.user.is_authenticated:
        current_user = get_object_or_404(User,username=request.user)
        profile = current_user.userprofile        
            
    else:
        
        profile= None
    
    archive = Post.objects.filter(created_on__year=year, created_on__month=month)
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    topics = Post.topicsCount()
    page = Paginator(archive,5)
    page_numb = request.GET.get('page',1)
    page_obj = page.page(page_numb)
    most_views = Post.objects.all().order_by('-views')[0:5]
    context = {'archive':archive, 'converted_list': converted_list,'year':year, 'monthfull':monthfull,'topics':topics,'page_obj':page_obj,'most_views':most_views, 'profile':profile}
    return render(request,'blog_app/archive.html', context)

def topicsPost(request, topic):
    if request.user.is_authenticated:
        current_user = get_object_or_404(User,username=request.user)
        profile = current_user.userprofile        
            
    else:
        
        profile= None
    topic_posts = Post.objects.filter(topics__name=topic)
    topics = Post.topicsCount()
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
   
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    page = Paginator(topic_posts,5)
    page_numb = request.GET.get('page',1)
    page_obj = page.page(page_numb)
    most_views = Post.objects.all().order_by('-views')[0:5]
    context = {'converted_list': converted_list,'topics':topics,'topic':topic_posts,'page_obj':page_obj,'most_views':most_views,'profile':profile}
    return render(request, 'blog_app/topic.html', context)

def profileDetail(request,user):
    if request.user.is_authenticated:
        current_user = get_object_or_404(User,username=user)
        profile = current_user.userprofile        
            
    else:
        current_user = get_object_or_404(User,username=user)
        profile= None
    
    recent_post = Post.objects.order_by('-created_on')[:3]
        
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    topics = Post.topicsCount()
    most_views = Post.objects.all().order_by('-views')[0:5]
    context = {'recent_post':recent_post,'converted_list':converted_list, 'topics':topics, 'most_views':most_views, 'profile':profile,'current_user':current_user}
    return render(request, 'blog_app\profile_detail.html', context)

def profileUpdate(request,user):
    if request.user.is_authenticated:
        current_user = get_object_or_404(User,username=user)
        profile = current_user.userprofile     
        form1=profileUpdateForm1(request.POST or None, instance=current_user)
        form2= profileUpdateForm2(request.POST or None, request.FILES or None, instance=profile)
        
        
    else:
        current_user = get_object_or_404(User,username=user)
        profile= None
    
    recent_post = Post.objects.order_by('-created_on')[:3]
        
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    topics = Post.topicsCount()
    most_views = Post.objects.all().order_by('-views')[0:5]
    
    if form1.is_valid() and form2.is_valid():
            
            form1.save()
            form2.save()
            messages.info(request,'Your profile has been updated secessfully.') 
    
    context = {'recent_post':recent_post,'converted_list':converted_list, 'topics':topics, 'most_views':most_views, 'profile':profile,'current_user':current_user,'form1':form1,'form2':form2}
    return render(request, 'blog_app\profile_update.html', context)

def changePassword(request,user):
    posts = Post.objects.all()
    most_views = Post.objects.all().order_by('-views')[0:5]
    
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
    topics = Post.topicsCount()
    
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    
    page = Paginator(posts,5)
    page_numb = request.GET.get('page',1)
    page_obj = page.page(page_numb)
    form =CustomPasswordChangeForm(user=request.user, data=request.POST)
    if request.user.is_authenticated:
        user = User.objects.get(username= request.user)
        profile = user.userprofile
        if form.is_valid():
            user = form.save()
            messages.info(request,'Your password has been changed scucessfully')
            return redirect('login')    
    else:
        profile= None
    
    context = {'form':form, 'converted_list':converted_list,'topics':topics,'page_obj':page_obj,'most_views':most_views, 'profile':profile}
    return render(request,'blog_app\change_password.html', context)

def membership(request):
    posts = Post.objects.all()
    most_views = Post.objects.all().order_by('-views')[0:5]
    
    six_months = timezone.now() - relativedelta(months=6)
    archive_list = Post.objects.filter(created_on__gte=six_months) \
        .annotate(year=ExtractYear('created_on'), month=ExtractMonth('created_on')) \
        .values('year', 'month') \
        .annotate(count=Count('id')) \
        .order_by('-year', '-month')
    topics = Post.topicsCount()
    
    converted_list = []
    for item in archive_list:
        month_num = item['month']
        month_name = calendar.month_name[month_num]
        # Create a new dictionary with the month name
        new_item = {'month_name': month_name, 'year': item['year'], 'count': item['count'], 'month':item['month']}
        converted_list.append(new_item)
    
    page = Paginator(posts,5)
    page_numb = request.GET.get('page',1)
    page_obj = page.page(page_numb)
    if request.user.is_authenticated:
        user = User.objects.get(username= request.user)
        profile = user.userprofile    
    else:
        profile= None
    context = {'posts':posts, 'converted_list':converted_list,'topics':topics,'page_obj':page_obj,'most_views':most_views, 'profile':profile}
    
    return render(request,'blog_app\membership.html', context)