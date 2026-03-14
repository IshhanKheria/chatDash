from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from ..models import Message
from ..serializers import MessageSerializer, MessageEditSerializer

User = get_user_model()


class MessagePagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_history(request, user_id):
    try:
        other_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    messages = Message.objects.filter(
        sender=request.user, receiver=other_user
    ) | Message.objects.filter(
        sender=other_user, receiver=request.user
    )
    messages = messages.select_related('sender', 'receiver').order_by('created_at')

    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)
    serializer = MessageSerializer(page, many=True)
    return paginator.get_paginated_response({'success': True, 'messages': serializer.data})


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def edit_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'success': False, 'message': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

    if message.sender != request.user:
        return Response({'success': False, 'message': 'You can only edit your own messages.'}, status=status.HTTP_403_FORBIDDEN)

    if message.is_deleted:
        return Response({'success': False, 'message': 'Cannot edit a deleted message.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MessageEditSerializer(data=request.data)
    if serializer.is_valid():
        message.content = serializer.validated_data['content']
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        return Response({'success': True, 'message': MessageSerializer(message).data})
    return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_message(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'success': False, 'message': 'Message not found.'}, status=status.HTTP_404_NOT_FOUND)

    if message.sender != request.user:
        return Response({'success': False, 'message': 'You can only delete your own messages.'}, status=status.HTTP_403_FORBIDDEN)

    if message.is_deleted:
        return Response({'success': False, 'message': 'Message already deleted.'}, status=status.HTTP_400_BAD_REQUEST)

    message.is_deleted = True
    message.deleted_at = timezone.now()
    message.save()
    return Response({'success': True, 'message': 'Message deleted.'})
