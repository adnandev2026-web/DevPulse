from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import ChatGroupForm, ChatMessageForm, SignInForm
from .models import ChatGroup, ChatMessage, GroupMembership


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control", "required": "required"})


def home(request):
    return render(request, "index.html")


def signin(request):
    if request.user.is_authenticated:
        return redirect("chat_list")

    form = SignInForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account was created successfully.")
        return redirect("chat_list")
    return render(request, "signin.html", {"form": form})


def chat_list(request):
    query = request.GET.get("q", "").strip()
    groups = ChatGroup.objects.annotate(follower_count=Count("followers"))
    if query:
        groups = groups.filter(Q(name__icontains=query) | Q(description__icontains=query))
    followed_ids = set()
    if request.user.is_authenticated:
        followed_ids = set(
            GroupMembership.objects.filter(user=request.user).values_list("group_id", flat=True)
        )
    return render(
        request,
        "chat.html",
        {"groups": groups, "query": query, "followed_ids": followed_ids},
    )


@login_required
def create_group(request):
    form = ChatGroupForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        group = form.save(commit=False)
        group.created_by = request.user
        group.save()
        GroupMembership.objects.create(group=group, user=request.user)
        messages.success(request, "Your group was created.")
        return redirect("chat_detail", group_id=group.pk)
    return render(request, "create_group.html", {"form": form})


def chat_detail(request, group_id):
    group = get_object_or_404(
        ChatGroup.objects.annotate(follower_count=Count("followers")),
        pk=group_id,
    )
    is_member = request.user.is_authenticated and GroupMembership.objects.filter(
        group=group, user=request.user
    ).exists()
    if not is_member:
        return render(request, "chat_detail.html", {"group": group, "is_member": False})

    form = ChatMessageForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        ChatMessage.objects.create(
            group=group,
            author=request.user,
            body=form.cleaned_data["body"].strip(),
        )
        return redirect("chat_detail", group_id=group.pk)

    chat_messages = group.messages.select_related("author").all()
    return render(
        request,
        "chat_detail.html",
        {
            "group": group,
            "is_member": True,
            "form": form,
            "chat_messages": chat_messages,
        },
    )


@login_required
@require_POST
def toggle_follow(request, group_id):
    group = get_object_or_404(ChatGroup, pk=group_id)
    membership, created = GroupMembership.objects.get_or_create(group=group, user=request.user)
    if not created:
        membership.delete()
        messages.info(request, f"You left {group.name}.")
    else:
        messages.success(request, f"You followed {group.name}.")
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("chat_list")


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    followed_groups = profile_user.followed_chat_groups.annotate(
        follower_count=Count("followers")
    )
    return render(
        request,
        "profile.html",
        {"profile_user": profile_user, "followed_groups": followed_groups},
    )
