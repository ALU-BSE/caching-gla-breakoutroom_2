#!/usr/bin/env python3
"""
Simple Cache Verification Script

Quick script to verify that caching is working correctly.
Run this after starting your Django server and Redis.
"""

import os
import sys
import django


def setup_django():
    """Setup Django environment for direct cache testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'safeboda.settings')
    django.setup()


def test_django_cache():
    """Test Django cache directly"""
    from django.core.cache import cache
    
    print("🧪 Testing Django Cache Configuration...")
    
    # Test basic cache operations
    test_key = 'test_cache_key'
    test_value = 'Hello, Cache!'
    
    try:
        # Set a value
        cache.set(test_key, test_value, 30)
        print(f"Cache SET: {test_key} = {test_value}")
        
        # Get the value
        cached_value = cache.get(test_key)
        if cached_value == test_value:
            print(f"Cache GET: {test_key} = {cached_value}")
        else:
            print(f"Cache GET failed: expected {test_value}, got {cached_value}")
        
        # Delete the value
        cache.delete(test_key)
        deleted_value = cache.get(test_key)
        if deleted_value is None:
            print(f"Cache DELETE: {test_key} successfully deleted")
        else:
            print(f"Cache DELETE failed: {test_key} still exists")
            
    except Exception as e:
        print(f"Cache test failed: {e}")
        print("Make sure Redis is running on localhost:6379")
        return False
    
    return True


def test_redis_connection():
    """Test Redis connection directly"""
    try:
        from django_redis import get_redis_connection
        redis_conn = get_redis_connection("default")
        
        # Test Redis ping
        pong = redis_conn.ping()
        if pong:
            print("Redis connection: PONG received")
        else:
            print("Redis connection: No PONG received")
            
        # Test Redis info
        info = redis_conn.info()
        print(f"Redis version: {info.get('redis_version', 'Unknown')}")
        
        # Show current keys
        keys = redis_conn.keys('*')
        print(f"Current Redis keys: {len(keys)}")
        if keys:
            print(f"   Sample keys: {[k.decode('utf-8') if isinstance(k, bytes) else str(k) for k in keys[:5]]}")
        
        return True
        
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False


def test_cache_warm_up():
    """Test the cache warm-up functionality"""
    from django.core.management import call_command
    from io import StringIO
    
    print("\nTesting Cache Warm-up...")
    
    try:
        # Capture command output
        out = StringIO()
        call_command('warm_cache', '--models', 'users', stdout=out)
        output = out.getvalue()
        print(output)
        
        if "Successfully warmed cache" in output:
            print("Cache warm-up completed successfully")
        else:
            print("Cache warm-up completed but with warnings")
            
    except Exception as e:
        print(f"Cache warm-up failed: {e}")


def verify_model_caching():
    """Test that model operations trigger cache invalidation"""
    from django.core.cache import cache
    from users.models import User
    
    print("\nTesting Model Cache Invalidation...")
    
    try:
        # Check if user_list is cached
        user_list_before = cache.get('user_list')
        if user_list_before:
            print(f"Found cached user_list with {len(user_list_before)} users")
        else:
            print("No user_list in cache")
        
        # Create a test user to trigger cache invalidation
        print(" Creating test user to trigger cache invalidation...")
        user = User.objects.create_user(
            email='cache_test@example.com',
            password='testpass123',
            user_type='passenger'
        )
        
        # Check if cache was cleared
        user_list_after = cache.get('user_list')
        if user_list_after is None:
            print("Cache invalidation working: user_list was cleared")
        else:
            print(" Cache may not be invalidating properly")
        
        # Clean up
        user.delete()
        print("  Test user cleaned up")
        
    except Exception as e:
        print(f" Model caching test failed: {e}")


def main():
    """Main verification function"""
    print(" SafeBoda Cache Verification")
    print("=" * 40)
    
    # Setup Django
    setup_django()
    
    # Test cache configuration
    cache_ok = test_django_cache()
    if not cache_ok:
        print("\n Basic cache tests failed. Check your Redis setup.")
        sys.exit(1)
    
    # Test Redis connection
    redis_ok = test_redis_connection()
    if not redis_ok:
        print("\n Redis connection failed. Make sure Redis is running.")
        sys.exit(1)
    
    # Test warm-up command
    test_cache_warm_up()
    
    # Test model cache invalidation
    verify_model_caching()
    
    print("\n Cache verification completed!")
    print("\nNext steps:")
    print("1. Start your Django server: python manage.py runserver")
    print("2. Run performance tests: python test_cache_performance.py")
    print("3. Check cache stats: curl http://localhost:8000/api/cache-stats/")


if __name__ == "__main__":
    main()