"""Create service associated service views.

This views does not start with rest since them are associated with auxiliary
service related actions.
"""
from loguru import logger
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from pumpwood_communication.cache import default_cache
from pumpwood_djangoauth.permissions import PumpwoodIsSuperuser


@api_view(['POST'])
@permission_classes([PumpwoodIsSuperuser])
def view__clear_diskcache(request):
    """End-point to clear diskcache."""
    default_cache.clear()
    logger.warning('Pumpwood [pumpwood-auth-app] service cache cleared')
    return Response(True)


@api_view(['GET'])
@permission_classes([AllowAny])
def view__health_check(request):
    """End-point to be used as health_check."""
    return Response(True)
