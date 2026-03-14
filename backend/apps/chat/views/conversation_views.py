from django.db.models import Q, Max, Subquery, OuterRef
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Message
from apps.accounts.serializers import UserSerializer

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    """Return list of users the current user has exchanged messages with."""
    user = request.user

    # Get all users who have exchanged messages with current user
    sent_to = Message.objects.filter(sender=user, receiver__isnull=False).values_list('receiver_id', flat=True)
    received_from = Message.objects.filter(receiver=user).values_list('sender_id', flat=True)
    partner_ids = set(list(sent_to) + list(received_from))
    partners = User.objects.filter(id__in=partner_ids)

    return Response({'success': True, 'conversations': UserSerializer(partners, many=True).data})
