from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topics, Message
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm


# Create your views here.
def login_view(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except user is None:
            messages.error(request, " Not valid user")
            return redirect('login')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            messages.success(request, 'login successfull')
            return redirect('home')
        else:
            messages.error(request, 'incorrect username or password')
    return render(request, "base/login_register.html",  {'page': page})


def logout_view(request):
    logout(request)
    messages.success(request, 'Come back soon')
    return redirect('home')


def register_view(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            '''creates an instance of the model but does not save
            it to the database immediately we can make changes to it'''
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
            return redirect('register')

    context = {
        'form': form
    }
    return render(request, 'base/login_register.html', context)


def index(request):
    q = request.GET.get("q", "")
    topics = Topics.objects.all()[0:3]
    # we get the q from the dynamic link, which is then quried using Q
    # In search, the value is passed to q, by GEt.get then it is quried
    room = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    room_count = room.count()
    message_room = Message.objects.filter(
        Q(room__topic__name__icontains=q) |
        Q(user__username__icontains=q) |
        Q(body__icontains=q)
    )

    context = {"room": room,
               "topics": topics,
               "room_count": room_count,
               'message_room': message_room
               }
    return render(request, "base/index.html", context)


def room(request, id):
    room = Room.objects.get(id=id)
    participents = room.participants.all()
    topics = Topics.objects.all()

    # room_messages will be list of all messages objects
    room_messages = room.message_set.all()
    if request.method == "POST":
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', id=room.id)
    context = {"room": room,
               'room_messages': room_messages,
               'participents': participents,
               'topics': topics
               }
    return render(request, "base/room.html", context)


def profile_view(request, id):
    user = User.objects.get(id=id)
    room = user.room_set.all()
    message_room = user.message_set.all()
    topics = Topics.objects.all()
    context = {
        'user': user,
        'room': room,
        'message_room': message_room,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def create_room(request):
    form = RoomForm()
    topics = Topics.objects.all()
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topics.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect("home")
    context = {"form": form,
               'topics': topics}
    return render(request, "base/room_form.html", context)


@login_required(login_url='login')
def update_room(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse("Only host can change the setting")

    """pass the info of excisting room through the instance ,
    the romm is accessed through id passed and then it is use to
    assess the from by the instance"""
#    if request.method == "POST":
#         # to access and edit the same room we pass instance to the form
#         form = RoomForm(request.POST, instance=room)
#         if form.is_valid():
#             form.save()
#             return redirect("home")

    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topics.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect("home")
    context = {"form": form,
               'room': room}
    return render(request, "base/room_form.html", context)


@login_required(login_url='login')
def delete_room(request, id):
    room = Room.objects.get(id=id)
    if request.user != room.host:
        return HttpResponse("Only host can change the setting")
    referrer = request.META.get("HTTP_REFERER", "home")
    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": room,
                                                "referrer": referrer})


@login_required(login_url='login')
def delete_message(request, id):
    message = Message.objects.get(id=id)
    if request.user != message.user:
        return HttpResponse("Only host can change the setting")
    referrer = request.META.get("HTTP_REFERER", "home")
    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "base/delete.html", {"obj": message,
                                                "referrer": referrer})


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile_view', id=user.id)
    context = {
        'form': form
    }
    return render(request, 'base/update_users.html',  context)


def topic_page(request):
    q = request.GET.get("q", "")
    topic = Topics.objects.filter(name__icontains=q)
    context = {
        'topics': topic
    } 
    return render(request, 'base/topics.html', context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {
        'room_messages': room_messages
    }
    return render(request, "base/activity.html", context)
