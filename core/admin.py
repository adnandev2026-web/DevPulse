from django.contrib import admin

from .models import ChatGroup, ChatMessage, GroupMembership


@admin.register(ChatGroup)
class ChatGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name", "description", "created_by__username")


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ("group", "user", "joined_at")
    search_fields = ("group__name", "user__username")


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("group", "author", "created_at")
    search_fields = ("group__name", "author__username", "body")
