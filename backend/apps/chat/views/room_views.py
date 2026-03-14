from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from ..models import Room, RoomMember, Message
from ..serializers import (
    RoomSerializer, RoomCreateSerializer,
    RoomMemberSerializer, MessageSerializer,
)

User = get_user_model()


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def rooms(request):
    if request.method == 'GET':
        user_rooms = Room.objects.filter(members__user=request.user).select_related('creator')
        return Response({'success': True, 'rooms': RoomSerializer(user_rooms, many=True).data})

    serializer = RoomCreateSerializer(data=request.data)
    if serializer.is_valid():
        room = serializer.save(creator=request.user)
        RoomMember.objects.create(room=room, user=request.user)
        return Response({'success': True, 'room': RoomSerializer(room).data}, status=status.HTTP_201_CREATED)
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_detail(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({'success': False, 'message': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not RoomMember.objects.filter(room=room, user=request.user).exists():
        return Response({'success': False, 'message': 'You are not a member of this room.'}, status=status.HTTP_403_FORBIDDEN)

    members = RoomMember.objects.filter(room=room).select_related('user')
    return Response({
        'success': True,
        'room': RoomSerializer(room).data,
        'members': RoomMemberSerializer(members, many=True).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_member(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({'success': False, 'message': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not RoomMember.objects.filter(room=room, user=request.user).exists():
        return Response({'success': False, 'message': 'You are not a member of this room.'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    _, created = RoomMember.objects.get_or_create(room=room, user=user)
    if not created:
        return Response({'success': False, 'message': 'User is already a member.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'success': True, 'message': f'{user.username} added to room.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_member(request, room_id, user_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({'success': False, 'message': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Only creator can remove others, anyone can remove themselves
    if int(user_id) != request.user.id and room.creator != request.user:
        return Response({'success': False, 'message': 'Only the room creator can remove other members.'}, status=status.HTTP_403_FORBIDDEN)

    if int(user_id) == room.creator_id:
        member_count = RoomMember.objects.filter(room=room).count()
        if member_count > 1:
            return Response({'success': False, 'message': 'Room creator cannot leave while other members are present.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        membership = RoomMember.objects.get(room=room, user_id=user_id)
        membership.delete()
        return Response({'success': True, 'message': 'Member removed.'})
    except RoomMember.DoesNotExist:
        return Response({'success': False, 'message': 'User is not a member.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def room_messages(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
    except Room.DoesNotExist:
        return Response({'success': False, 'message': 'Room not found.'}, status=status.HTTP_404_NOT_FOUND)

    if not RoomMember.objects.filter(room=room, user=request.user).exists():
        return Response({'success': False, 'message': 'You are not a member of this room.'}, status=status.HTTP_403_FORBIDDEN)

    messages = Message.objects.filter(room=room).select_related('sender').order_by('created_at')
    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)
    serializer = MessageSerializer(page, many=True)
    return paginator.get_paginated_response({'success': True, 'messages': serializer.data})
