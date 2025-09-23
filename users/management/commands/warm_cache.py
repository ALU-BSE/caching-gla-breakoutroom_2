from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from users.models import User, Passenger, Rider
from users.serializers import UserSerializer


class Command(BaseCommand):
    help = 'Warm up the cache with frequently accessed data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=3600,
            help='Cache timeout in seconds (default: 3600)'
        )
        parser.add_argument(
            '--models',
            nargs='+',
            choices=['users', 'passengers', 'riders'],
            default=['users', 'passengers', 'riders'],
            help='Models to warm up (default: all)'
        )

    def handle(self, *args, **options):
        timeout = options['timeout']
        models_to_warm = options['models']
        
        total_cached = 0
        
        if 'users' in models_to_warm:
            total_cached += self.warm_users_cache(timeout)
        
        if 'passengers' in models_to_warm:
            total_cached += self.warm_passengers_cache(timeout)
        
        if 'riders' in models_to_warm:
            total_cached += self.warm_riders_cache(timeout)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully warmed cache with {total_cached} items (timeout: {timeout}s)'
            )
        )

    def warm_users_cache(self, timeout):
        """Pre-cache user data"""
        self.stdout.write('Warming users cache...')
        
        # Pre-cache user list
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        cache.set('user_list', serializer.data, timeout=timeout)
        
        cached_count = 1  # user_list
        
        # Pre-cache individual users
        for user in users:
            user_data = UserSerializer(user).data
            cache.set(f'user_{user.id}', user_data, timeout=timeout)
            cached_count += 1
        
        self.stdout.write(f'  - Cached {cached_count} user items')
        return cached_count

    def warm_passengers_cache(self, timeout):
        """Pre-cache passenger data"""
        self.stdout.write('Warming passengers cache...')
        
        try:
            passengers = Passenger.objects.select_related('user').all()
            
            # Create simple passenger data structure
            passenger_data = []
            for passenger in passengers:
                passenger_data.append({
                    'id': passenger.id,
                    'passenger_id': passenger.passenger_id,
                    'user_email': passenger.user.email,
                    'preferred_payment_method': passenger.preferred_payment_method,
                    'home_address': passenger.home_address,
                })
            
            cache.set('passenger_list', passenger_data, timeout=timeout)
            
            cached_count = 1  # passenger_list
            
            # Pre-cache individual passengers
            for i, passenger in enumerate(passengers):
                cache.set(f'passenger_{passenger.id}', passenger_data[i], timeout=timeout)
                cached_count += 1
            
            self.stdout.write(f'  - Cached {cached_count} passenger items')
            return cached_count
            
        except Exception as e:
            self.stdout.write(f'  - Error warming passengers cache: {e}')
            return 0

    def warm_riders_cache(self, timeout):
        """Pre-cache rider data"""
        self.stdout.write('Warming riders cache...')
        
        try:
            riders = Rider.objects.select_related('user').all()
            
            # Create simple rider data structure
            rider_data = []
            for rider in riders:
                rider_data.append({
                    'id': rider.id,
                    'user_email': rider.user.email,
                    'user_id': rider.user.id,
                })
            
            cache.set('rider_list', rider_data, timeout=timeout)
            
            cached_count = 1  # rider_list
            
            # Pre-cache individual riders
            for i, rider in enumerate(riders):
                cache.set(f'rider_{rider.id}', rider_data[i], timeout=timeout)
                cached_count += 1
            
            self.stdout.write(f'  - Cached {cached_count} rider items')
            return cached_count
            
        except Exception as e:
            self.stdout.write(f'  - Error warming riders cache: {e}')
            return 0