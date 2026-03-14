from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'success': False,
            'message': response.data.get('detail', str(response.data)),
            'errors': response.data if isinstance(response.data, dict) else None,
        }
    else:
        response = Response(
            {'success': False, 'message': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
