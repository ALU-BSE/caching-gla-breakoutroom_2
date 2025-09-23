#!/usr/bin/env python3
"""
Cache Performance Testing Script

This script tests the performance improvement provided by caching
for the SafeBoda Django application.

Usage:
    python test_cache_performance.py
"""

import requests
import time
import statistics
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


class CachePerformanceTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        
    def test_endpoint_performance(self, endpoint, num_requests=5):
        """Test performance of an endpoint with multiple requests"""
        url = f"{self.api_base}/{endpoint}/"
        times = []
        
        print(f"\nTesting {endpoint} endpoint...")
        print(f"🔗 URL: {url}")
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                response = requests.get(url)
                end_time = time.time()
                
                request_time = end_time - start_time
                times.append(request_time)
                
                status_emoji = "Succcess" if response.status_code == 200 else "Error"
                cache_status = "HIT" if i > 0 else "MISS (expected)"
                
                print(f"  Request {i+1}: {status_emoji} {request_time:.4f}s ({cache_status})")
                
                # Small delay between requests
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"  Request {i+1}: Error - {e}")
                continue
        
        if times:
            avg_time = statistics.mean(times)
            first_request = times[0]
            subsequent_avg = statistics.mean(times[1:]) if len(times) > 1 else first_request
            speedup = first_request / subsequent_avg if subsequent_avg > 0 else 1
            
            print(f"  First request (cache miss): {first_request:.4f}s")
            print(f"  Subsequent avg (cache hit): {subsequent_avg:.4f}s")
            print(f"  Speedup: {speedup:.2f}x")
            
            return {
                'endpoint': endpoint,
                'first_request_time': first_request,
                'subsequent_avg_time': subsequent_avg,
                'speedup': speedup,
                'all_times': times
            }
        
        return None
    
    def concurrent_load_test(self, endpoint, concurrent_users=10, requests_per_user=5):
        """Test concurrent access to cached endpoints"""
        print(f"\n Concurrent Load Test: {endpoint}")
        print(f"👥 {concurrent_users} concurrent users, {requests_per_user} requests each")
        
        url = f"{self.api_base}/{endpoint}/"
        
        def make_request(user_id):
            times = []
            for i in range(requests_per_user):
                try:
                    start_time = time.time()
                    response = requests.get(url)
                    end_time = time.time()
                    
                    request_time = end_time - start_time
                    times.append(request_time)
                    
                except requests.exceptions.RequestException:
                    continue
            
            return times
        
        all_times = []
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_request, i) for i in range(concurrent_users)]
            
            for future in as_completed(futures):
                try:
                    times = future.result()
                    all_times.extend(times)
                except Exception as e:
                    print(f"Thread error: {e}")
        
        if all_times:
            avg_time = statistics.mean(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            
            print(f"  Total requests: {len(all_times)}")
            print(f"  Average time: {avg_time:.4f}s")
            print(f"  Fastest: {min_time:.4f}s")
            print(f"  Slowest: {max_time:.4f}s")
            
            return {
                'total_requests': len(all_times),
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
            }
        
        return None
    
    def get_cache_stats(self):
        """Get cache statistics from the API"""
        try:
            url = f"{self.api_base}/cache-stats/"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get cache stats: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting cache stats: {e}")
            return None
    
    def clear_cache_and_test(self):
        """Clear cache by restarting and test fresh performance"""
        print("\n🧹 Testing with cleared cache...")
        print("ℹ️  Note: In production, you might need to clear Redis manually")
        
    def run_comprehensive_test(self):
        """Run comprehensive cache performance tests"""
        print("🎯 SafeBoda Cache Performance Test Suite")
        print("=" * 50)
        
        # Check if server is running
        try:
            response = requests.get(f"{self.base_url}/admin/")  # Try admin to check server
            print(f"Server is running at {self.base_url}")
        except requests.exceptions.RequestException:
            print(f"Server is not reachable at {self.base_url}")
            print("Please start the Django development server:")
            print("  python manage.py runserver")
            return
        
        # Get initial cache stats
        print("\nInitial Cache Statistics:")
        cache_stats = self.get_cache_stats()
        if cache_stats:
            print(f"  Total cache keys: {cache_stats.get('total_keys', 0)}")
            print(f"  Cache timeout: {cache_stats.get('cache_timeout', 0)}s")
        
        # Test individual endpoints
        endpoints = ['users', 'passengers', 'riders']
        results = []
        
        for endpoint in endpoints:
            result = self.test_endpoint_performance(endpoint, num_requests=5)
            if result:
                results.append(result)
        
        # Concurrent load tests
        print(f"\n{'='*20} LOAD TESTING {'='*20}")
        for endpoint in endpoints:
            self.concurrent_load_test(endpoint, concurrent_users=5, requests_per_user=3)
        
        # Final cache stats
        print(f"\n{'='*20} FINAL RESULTS {'='*20}")
        cache_stats = self.get_cache_stats()
        if cache_stats:
            print(f"Final Cache Statistics:")
            print(f"  Total cache keys: {cache_stats.get('total_keys', 0)}")
            print(f"  User keys: {cache_stats.get('user_related_keys', 0)}")
            print(f"  Passenger keys: {cache_stats.get('passenger_related_keys', 0)}")
            print(f"  Rider keys: {cache_stats.get('rider_related_keys', 0)}")
        
        # Summary
        print(f"\nPerformance Summary:")
        for result in results:
            speedup = result['speedup']
            emoji = "Fast" if speedup > 2 else "Fast" if speedup > 1.5 else "Up"
            print(f"  {emoji} {result['endpoint']}: {speedup:.2f}x speedup")
        
        return results


def main():
    """Main function to run cache performance tests"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    tester = CachePerformanceTester(base_url)
    results = tester.run_comprehensive_test()
    
    # Save results to file
    if results:
        with open('cache_performance_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to cache_performance_results.json")


if __name__ == "__main__":
    main()