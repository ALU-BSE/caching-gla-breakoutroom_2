# SafeBoda Caching Implementation

This document provides a comprehensive guide to the caching implementation for the SafeBoda Django application.

## 🚀 Quick Start

1. **Start Redis using Docker:**
   ```bash
   docker run -d -p 6379:6379 --name redis-cache redis:alpine
   ```

2. **Verify cache setup:**
   ```bash
   python verify_cache.py
   ```

3. **Warm up the cache:**
   ```bash
   python manage.py warm_cache
   ```

4. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

5. **Run performance tests:**
   ```bash
   python test_cache_performance.py
   ```

## 📋 Features Implemented

###  Basic Cache Configuration
- Redis backend configured in `settings.py`
- Cache timeout of 5 minutes (300 seconds)
- Django-Redis integration

###  View-Level Caching
- **UserViewSet**: Cached list() and retrieve() methods
- **PassengerViewSet**: Complete caching implementation
- **RiderViewSet**: Complete caching implementation
- Cache performance monitoring with decorators

###  Cache Invalidation
- Manual invalidation in ViewSet CRUD operations
- Signal-based automatic invalidation
- Proper cache key management

###  Cache Performance Monitoring
- Performance decorator for timing cache operations
- Cache statistics endpoint: `/api/cache-stats/`
- Logging for cache hits/misses

###  Cache Management
- Management command: `python manage.py warm_cache`
- Cache verification script: `verify_cache.py`
- Performance testing script: `test_cache_performance.py`

## 🎯 API Endpoints

| Endpoint | Description | Cached |
|----------|-------------|--------|
| `/api/users/users/` | List all users |  |
| `/api/users/users/{id}/` | Get user by ID |  |
| `/api/users/passengers/` | List all passengers |  |
| `/api/users/passengers/{id}/` | Get passenger by ID |  |
| `/api/users/riders/` | List all riders |  |
| `/api/users/riders/{id}/` | Get rider by ID |  |
| `/api/users/cache-stats/` | Cache statistics |  |

## 🔧 Configuration

### Redis Settings

```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'TIMEOUT': 60,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

CACHE_TTL = 5 * 60  # 5 minutes
```

### Cache Keys Structure

- `user_list` - List of all users
- `user_{id}` - Individual user data
- `passenger_list` - List of all passengers
- `passenger_{id}` - Individual passenger data
- `rider_list` - List of all riders
- `rider_{id}` - Individual rider data

## 🧪 Testing

### Verify Cache Setup
```bash
python verify_cache.py
```
This script tests:
- Django cache configuration
- Redis connection
- Cache warm-up command
- Model cache invalidation

### Performance Testing
```bash
python test_cache_performance.py
```
This script:
- Tests cache performance for all endpoints
- Runs concurrent load tests
- Measures cache hit/miss ratios
- Saves results to `cache_performance_results.json`

### Manual Testing

1. **Test cache hit/miss:**
   ```bash
   # First call (cache miss)
   curl http://localhost:8000/api/users/
   
   # Second call (cache hit - should be faster)
   curl http://localhost:8000/api/users/
   ```

2. **Check cache statistics:**
   ```bash
   curl http://localhost:8000/api/cache-stats/
   ```

3. **Test cache invalidation:**
   ```bash
   # Cache the users list
   curl http://localhost:8000/api/users/
   
   # Create a new user (this should invalidate the cache)
   curl -X POST http://localhost:8000/api/users/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "user_type": "passenger"}'
   
   # Fetch users again (should be a cache miss)
   curl http://localhost:8000/api/users/
   ```

##  Cache Management Commands

### Warm Cache
```bash
# Warm all models
python manage.py warm_cache

# Warm specific models
python manage.py warm_cache --models users passengers

# Set custom timeout
python manage.py warm_cache --timeout 3600
```

### Clear Cache (Redis CLI)
```bash
# Connect to Redis
redis-cli

# Clear all keys
FLUSHALL

# Clear specific keys
DEL user_list
DEL user_1
```

##  Cache Invalidation Strategy

### Automatic Invalidation (Signals)
- Model saves trigger cache invalidation
- Model deletes trigger cache invalidation
- Related model changes invalidate parent caches

### Manual Invalidation (ViewSets)
- `perform_create()` clears list caches
- `perform_update()` clears list and individual caches
- `perform_destroy()` clears list and individual caches

### Cache Hierarchies
- User changes invalidate user caches
- Passenger changes invalidate passenger AND user caches
- Rider changes invalidate rider AND user caches

##  Performance Monitoring

### Cache Performance Decorator
```python
@cache_performance("endpoint_name")
def cached_method(self, request, *args, **kwargs):
    # Method implementation
```

### Logging
- Cache hits/misses are logged
- Performance timing is logged
- Cache invalidation events are logged

### Metrics Available
- Cache hit/miss ratios
- Request timing (with/without cache)
- Cache key counts by type
- Cache timeout settings

## 🛠️ Advanced Features

### Cache Tagging (Concept)
The implementation includes a conceptual cache tagging system for better invalidation:

```python
def cache_with_tags(key, data, tags, timeout=300):
    cache.set(key, data, timeout)
    for tag in tags:
        tagged_keys = cache.get(f'tag_{tag}', set())
        tagged_keys.add(key)
        cache.set(f'tag_{tag}', tagged_keys, timeout)

def invalidate_by_tag(tag):
    tagged_keys = cache.get(f'tag_{tag}', set())
    for key in tagged_keys:
        cache.delete(key)
    cache.delete(f'tag_{tag}')
```

### Write-Through Pattern
The implementation uses cache-aside pattern by default, but write-through is demonstrated:

```python
def perform_update(self, serializer):
    super().perform_update(serializer)
    
    # Write-through: immediately update cache
    user_data = self.get_serializer(serializer.instance).data
    cache_key = f"user_{serializer.instance.id}"
    cache.set(cache_key, user_data, timeout=settings.CACHE_TTL)
```

##  Production Considerations

### Security
- Cache keys don't contain sensitive data
- User permissions still enforced (cache is data-only)
- Redis should be secured in production

### Scaling
- Consider Redis Cluster for high availability
- Monitor Redis memory usage
- Implement cache size limits

### Monitoring
- Set up Redis monitoring
- Track cache hit ratios
- Monitor response times
- Alert on cache failures

##  Troubleshooting

### Common Issues

1. **Redis not running:**
   ```bash
   docker ps  # Check if redis-cache container is running
   docker start redis-cache  # Start if stopped
   ```

2. **Cache not working:**
   ```bash
   python verify_cache.py  # Run verification
   ```

3. **Performance not improving:**
   - Check Redis logs
   - Verify cache keys are being set
   - Check cache timeout settings

4. **Cache invalidation not working:**
   - Verify signals are connected in `apps.py`
   - Check logs for invalidation events
   - Test with `verify_cache.py`

### Debug Mode

Enable debug logging in `settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'users.views': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

##  Learning Outcomes Achieved

 Understanding different types of caching in Django  
 Implementing Redis-based caching for API endpoints  
 Creating cache invalidation strategies  
 Monitoring cache performance  
 Applying caching best practices  

##  Next Steps

1. Implement cache compression for large datasets
2. Add cache analytics dashboard
3. Implement distributed cache locks for concurrent updates
4. Add cache preloading based on user behavior patterns
5. Create cache versioning system for schema changes

---

**Note:** This implementation follows Django and Redis best practices and is suitable for development and production environments.