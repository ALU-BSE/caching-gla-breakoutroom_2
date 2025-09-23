from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import logging

from .models import User, Passenger, Rider

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """Clear user caches when a user is saved"""
    # Clear list cache
    cache.delete('user_list')
    
    # Clear individual user cache
    cache.delete(f'user_{instance.id}')
    
    logger.info(f"Invalidated cache for user {instance.id} after save")


@receiver(post_delete, sender=User)  
def invalidate_user_cache_on_delete(sender, instance, **kwargs):
    """Clear user caches when a user is deleted"""
    # Clear list cache
    cache.delete('user_list')
    
    # Clear individual user cache
    cache.delete(f'user_{instance.id}')
    
    logger.info(f"Invalidated cache for user {instance.id} after delete")


@receiver(post_save, sender=Passenger)
def invalidate_passenger_cache(sender, instance, **kwargs):
    """Clear passenger caches when a passenger is saved"""
    # Clear passenger list cache
    cache.delete('passenger_list')
    
    # Clear individual passenger cache
    cache.delete(f'passenger_{instance.id}')
    
    # Also clear related user cache
    cache.delete('user_list')
    cache.delete(f'user_{instance.user.id}')
    
    logger.info(f"Invalidated cache for passenger {instance.id} after save")


@receiver(post_delete, sender=Passenger)
def invalidate_passenger_cache_on_delete(sender, instance, **kwargs):
    """Clear passenger caches when a passenger is deleted"""
    # Clear passenger list cache
    cache.delete('passenger_list')
    
    # Clear individual passenger cache
    cache.delete(f'passenger_{instance.id}')
    
    # Also clear related user cache
    cache.delete('user_list')
    cache.delete(f'user_{instance.user.id}')
    
    logger.info(f"Invalidated cache for passenger {instance.id} after delete")


@receiver(post_save, sender=Rider)
def invalidate_rider_cache(sender, instance, **kwargs):
    """Clear rider caches when a rider is saved"""
    # Clear rider list cache
    cache.delete('rider_list')
    
    # Clear individual rider cache
    cache.delete(f'rider_{instance.id}')
    
    # Also clear related user cache
    cache.delete('user_list')
    cache.delete(f'user_{instance.user.id}')
    
    logger.info(f"Invalidated cache for rider {instance.id} after save")


@receiver(post_delete, sender=Rider)
def invalidate_rider_cache_on_delete(sender, instance, **kwargs):
    """Clear rider caches when a rider is deleted"""
    # Clear rider list cache
    cache.delete('rider_list')
    
    # Clear individual rider cache
    cache.delete(f'rider_{instance.id}')
    
    # Also clear related user cache
    cache.delete('user_list')
    cache.delete(f'user_{instance.user.id}')
    
    logger.info(f"Invalidated cache for rider {instance.id} after delete")