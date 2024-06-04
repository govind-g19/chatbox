from . import views
from django.urls import path

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.index, name='home'),
    path('room/<int:id>/', views.room, name='room'),
    path('create_room/', views.create_room, name='create_room'),
    path('profile_view/<int:id>/', views.profile_view, name='profile_view'),
    path('update_room/<int:id>/', views.update_room, name='update_room'),
    path('delete_room/<int:id>/', views.delete_room, name='delete_room'),
    path('delete_message/<int:id>/', views.delete_message,
         name='delete_message'),
    path('update_user/', views.update_user, name='update_user'),
    path('topics/', views.topic_page, name='topics'),
    path('activity/', views.activity_page, name='activity'),


]
