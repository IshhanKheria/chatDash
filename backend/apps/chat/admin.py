from django.contrib import admin
from .models import Message, Room, RoomMember


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'room', 'is_edited', 'is_deleted', 'created_at')
    list_filter = ('is_deleted', 'is_edited')
    search_fields = ('sender__username', 'receiver__username', 'content')
    raw_id_fields = ('sender', 'receiver', 'room')


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'creator', 'created_at')
    search_fields = ('name',)


@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'joined_at')
