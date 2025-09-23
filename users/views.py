from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
import functools
import time
import logging

from users.models import User, Passenger, Rider
from users.serializers import UserSerializer, PassengerSerializer, RiderSerializer


# Create your views here.

logger = logging.getLogger(__name__)


def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


def cache_performance(cache_name):
    """Decorator to monitor cache performance"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            logger.info(f"{cache_name}: {end_time - start_time:.4f}s")
            return result
        return wrapper
    return decorator


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @cache_performance("user_list_cache")
    def list(self, request, *args, **kwargs):
        """Cached list method for users"""
        # Step 1: Create cache key
        cache_key = get_cache_key('user_list')
        
        # Step 2: Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        # Step 3: Get fresh data
        response = super().list(request, *args, **kwargs)
        
        # Step 4: Store in cache
        cache.set(cache_key, response.data, timeout=getattr(settings, 'CACHE_TTL', 300))
        
        return response
    
    @cache_performance("user_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        """Cached retrieve method for individual users"""
        user_id = kwargs.get('pk')
        cache_key = get_cache_key('user', user_id)
        
        # Try to get from cache
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        # Get fresh data
        response = super().retrieve(request, *args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, response.data, timeout=getattr(settings, 'CACHE_TTL', 300))
        
        return response
    
    def perform_create(self, serializer):
        """Clear relevant caches when creating a user"""
        # Clear list cache
        cache.delete('user_list')
        logger.info("Cleared user_list cache after create")
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Clear relevant caches when updating a user"""
        # Clear both list and individual caches
        user_id = serializer.instance.id
        cache.delete('user_list')
        cache.delete(f'user_{user_id}')
        logger.info(f"Cleared caches for user {user_id} after update")
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Clear relevant caches when deleting a user"""
        user_id = instance.id
        cache.delete('user_list')
        cache.delete(f'user_{user_id}')
        logger.info(f"Cleared caches for user {user_id} after delete")
        super().perform_destroy(instance)


class PassengerViewSet(viewsets.ModelViewSet):
    queryset = Passenger.objects.select_related('user').all()
    serializer_class = PassengerSerializer
    
    @cache_performance("passenger_list_cache")
    def list(self, request, *args, **kwargs):
        """Cached list method for passengers"""
        cache_key = get_cache_key('passenger_list')
        
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        response = super().list(request, *args, **kwargs)
        
        cache.set(cache_key, response.data, timeout=getattr(settings, 'CACHE_TTL', 300))
        
        return response
    
    @cache_performance("passenger_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        """Cached retrieve method for individual passengers"""
        passenger_id = kwargs.get('pk')
        cache_key = get_cache_key('passenger', passenger_id)
        
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        
        cache.set(cache_key, response.data, timeout=getattr(settings, 'CACHE_TTL', 300))
        
        return response
    
    def perform_create(self, serializer):
        """Clear relevant caches when creating a passenger"""
        cache.delete('passenger_list')
        cache.delete('user_list')  # Also clear user list since passengers are related to users
        logger.info("Cleared passenger_list and user_list cache after create")
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Clear relevant caches when updating a passenger"""
        passenger_id = serializer.instance.id
        cache.delete('passenger_list')
        cache.delete(f'passenger_{passenger_id}')
        cache.delete('user_list')
        cache.delete(f'user_{serializer.instance.user.id}')
        logger.info(f"Cleared caches for passenger {passenger_id} after update")
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Clear relevant caches when deleting a passenger"""
        passenger_id = instance.id
        cache.delete('passenger_list')
        cache.delete(f'passenger_{passenger_id}')
        cache.delete('user_list')
        cache.delete(f'user_{instance.user.id}')
        logger.info(f"Cleared caches for passenger {passenger_id} after delete")
        super().perform_destroy(instance)


class RiderViewSet(viewsets.ModelViewSet):
    queryset = Rider.objects.select_related('user').all()
    serializer_class = RiderSerializer
    
    @cache_performance("rider_list_cache")
    def list(self, request, *args, **kwargs):
        """Cached list method for riders"""
        cache_key = get_cache_key('rider_list')
        
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        response = super().list(request, *args, **kwargs)
        
        cache.set(cache_key, response.data, timeout=getattr(settings, 'CACHE_TTL', 300))
        
        return response
    
    @cache_performance("rider_detail_cache")
    def retrieve(self, request, *args, **kwargs):
        """Cached retrieve method for individual riders"""
        rider_id = kwargs.get('pk')
        cache_key = get_cache_key('rider', rider_id)
        
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        
        cache.set(cache_key, response.data, timeout=getattr(settings, 'CACHE_TTL', 300))
        
        return response
    
    def perform_create(self, serializer):
        """Clear relevant caches when creating a rider"""
        cache.delete('rider_list')
        cache.delete('user_list')  # Also clear user list since riders are related to users
        logger.info("Cleared rider_list and user_list cache after create")
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Clear relevant caches when updating a rider"""
        rider_id = serializer.instance.id
        cache.delete('rider_list')
        cache.delete(f'rider_{rider_id}')
        cache.delete('user_list')
        cache.delete(f'user_{serializer.instance.user.id}')
        logger.info(f"Cleared caches for rider {rider_id} after update")
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Clear relevant caches when deleting a rider"""
        rider_id = instance.id
        cache.delete('rider_list')
        cache.delete(f'rider_{rider_id}')
        cache.delete('user_list')
        cache.delete(f'user_{instance.user.id}')
        logger.info(f"Cleared caches for rider {rider_id} after delete")
        super().perform_destroy(instance)


@api_view(['GET'])
def cache_stats(request):
    """Endpoint to show cache statistics"""
    try:
        # Get all cache keys (this is Redis-specific)
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Get all keys
        all_keys = redis_conn.keys('*')
        cache_keys = [key.decode('utf-8') if isinstance(key, bytes) else str(key) for key in all_keys]
        
        # Filter for our application keys
        user_keys = [key for key in cache_keys if 'user' in key]
        passenger_keys = [key for key in cache_keys if 'passenger' in key]
        rider_keys = [key for key in cache_keys if 'rider' in key]
        
        stats = {
            'total_keys': len(cache_keys),
            'user_related_keys': len(user_keys),
            'passenger_related_keys': len(passenger_keys),
            'rider_related_keys': len(rider_keys),
            'cache_keys': {
                'users': user_keys[:5],
                'passengers': passenger_keys[:5],
                'riders': rider_keys[:5],
            },
            'cache_timeout': getattr(settings, 'CACHE_TTL', 300),
        }
        
        return Response(stats)
    except Exception as e:
        return Response({
            'error': str(e),
            'message': 'Unable to fetch cache statistics'
        })
