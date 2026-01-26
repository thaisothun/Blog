from django.urls import path
from . import views

urlpatterns= [
    path('', views.index, name='index'),
    path("register/", views.register, name= "register"),
    path("login/", views.login, name= "login"),
    path("home/", views.home, name= "home"),
    path("logout/<int:pk>/", views.logOutPost, name= "logoutpost"),
    path("logout/", views.logOutHome, name= "logouthome"),
    path("detail-content/<int:pk>/", views.detailContent, name='detail-content'),
    path("likepost/<int:pk>/", views.likePost, name='like-post'),
    path("comments/<int:pk>/", views.commentPost, name='comment-post'),
    path("search/result/", views.searchPost, name='search-result'),
    path("archive/<int:year>/<str:month>/", views.archivePost, name='archive'),
    path("topics/<str:topic>/", views.topicsPost, name='topic'),
    path("profile_detail/<str:user>/", views.profileDetail, name='profile_detail'),
    path("profile_update/<str:user>/", views.profileUpdate, name='profile_update'),
    path("change_password/<str:user>/", views.changePassword, name='change_password'),
    path("membership/", views.membership, name='membership'),
]