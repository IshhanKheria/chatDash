from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Message, Room, RoomMember

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = (
            'id', 'sender_id', 'sender_username', 'receiver_id', 'receiver_username',
            'room_id', 'content', 'is_edited', 'is_deleted',
            'edited_at', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'sender_id', 'is_edited', 'is_deleted',
            'edited_at', 'created_at', 'updated_at',
        )

    def get_content(self, obj):
        return obj.get_content()


class MessageCreateSerializer(serializers.Serializer):
    receiver_id = serializers.IntegerField(required=False, allow_null=True)
    room_id = serializers.IntegerField(required=False, allow_null=True)
    content = serializers.CharField(min_length=1, max_length=5000)

    def validate(self, attrs):
        if not attrs.get('receiver_id') and not attrs.get('room_id'):
            raise serializers.ValidationError('Either receiver_id or room_id is required.')
        return attrs


class MessageEditSerializer(serializers.Serializer):
    content = serializers.CharField(min_length=1, max_length=5000)


class RoomSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ('id', 'name', 'description', 'creator_id', 'creator_username', 'member_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'creator_id', 'created_at', 'updated_at')

    def get_member_count(self, obj):
        return obj.members.count()


class RoomCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ('name', 'description')

    def validate_name(self, value):
        if len(value.strip()) < 1:
            raise serializers.ValidationError('Room name cannot be empty.')
        return value.strip()


class RoomMemberSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = RoomMember
        fields = ('id', 'user_id', 'username', 'email', 'joined_at')
