#!/usr/bin/env python3
"""
Performance testing script to measure backend response times.
"""

import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor
import argparse

def test_endpoint(url, num_requests=10):
    """Test a single endpoint multiple times and return statistics."""
    response_times = []
    
    print(f"\n🧪 Testing {url}")
    print(f"Making {num_requests} requests...")
    
    for i in range(num_requests):
        start_time = time.time()
        try:
            response = requests.get(url, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                response_time = (end_time - start_time) * 1000  # Convert to ms
                response_times.append(response_time)
                print(f"  Request {i+1}: {response_time:.2f}ms (Size: {len(response.content)} bytes)")
            else:
                print(f"  Request {i+1}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"  Request {i+1}: Error - {str(e)}")
    
    if response_times:
        avg_time = statistics.mean(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        median_time = statistics.median(response_times)
        
        print(f"\n📊 Results for {url}:")
        print(f"  ✅ Successful requests: {len(response_times)}/{num_requests}")
        print(f"  ⚡ Average: {avg_time:.2f}ms")
        print(f"  🚀 Fastest: {min_time:.2f}ms")
        print(f"  🐌 Slowest: {max_time:.2f}ms")
        print(f"  📈 Median: {median_time:.2f}ms")
        
        return {
            'url': url,
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'median': median_time,
            'success_rate': len(response_times) / num_requests * 100
        }
    else:
        print(f"❌ All requests failed for {url}")
        return None

def concurrent_test(url, concurrent_requests=5):
    """Test concurrent requests to simulate load."""
    print(f"\n🔄 Concurrent test for {url}")
    print(f"Making {concurrent_requests} concurrent requests...")
    
    def single_request():
        start_time = time.time()
        try:
            response = requests.get(url, timeout=30)
            end_time = time.time()
            return (end_time - start_time) * 1000, response.status_code
        except Exception as e:
            return None, str(e)
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(single_request) for _ in range(concurrent_requests)]
        results = [future.result() for future in futures]
    
    total_time = (time.time() - start_time) * 1000
    
    successful_requests = [(time, status) for time, status in results if isinstance(time, (int, float))]
    
    if successful_requests:
        response_times = [time for time, status in successful_requests]
        avg_time = statistics.mean(response_times)
        
        print(f"  ✅ Successful: {len(successful_requests)}/{concurrent_requests}")
        print(f"  ⚡ Average response time: {avg_time:.2f}ms")
        print(f"  🕒 Total time: {total_time:.2f}ms")
        print(f"  📊 Requests per second: {len(successful_requests) / (total_time / 1000):.2f}")
    
    return successful_requests

def main():
    parser = argparse.ArgumentParser(description='Performance test for Flask backend')
    parser.add_argument('--base-url', default='http://127.0.0.1:5000', 
                       help='Base URL for testing (default: http://127.0.0.1:5000)')
    parser.add_argument('--requests', type=int, default=10,
                       help='Number of requests per endpoint (default: 10)')
    parser.add_argument('--concurrent', type=int, default=5,
                       help='Number of concurrent requests for load test (default: 5)')
    
    args = parser.parse_args()
    
    # Test endpoints
    endpoints = [
        '/',
        '/projects',
        '/blog',
        '/project/1',
        '/project/2',
    ]
    
    print("🚀 Backend Performance Test")
    print("=" * 50)
    
    results = []
    
    # Test each endpoint
    for endpoint in endpoints:
        url = args.base_url + endpoint
        result = test_endpoint(url, args.requests)
        if result:
            results.append(result)
        time.sleep(1)  # Small delay between tests
    
    # Run concurrent tests
    print("\n" + "=" * 50)
    print("🔄 CONCURRENT LOAD TESTS")
    print("=" * 50)
    
    for endpoint in endpoints[:3]:  # Test first 3 endpoints for concurrent load
        url = args.base_url + endpoint
        concurrent_test(url, args.concurrent)
        time.sleep(2)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 PERFORMANCE SUMMARY")
    print("=" * 50)
    
    if results:
        for result in results:
            status = "🟢" if result['avg'] < 100 else "🟡" if result['avg'] < 500 else "🔴"
            print(f"{status} {result['url']:30} {result['avg']:6.1f}ms (Success: {result['success_rate']:5.1f}%)")
        
        overall_avg = statistics.mean([r['avg'] for r in results])
        print(f"\n📊 Overall average response time: {overall_avg:.2f}ms")
        
        # Performance rating
        if overall_avg < 100:
            print("🚀 EXCELLENT performance!")
        elif overall_avg < 300:
            print("✅ GOOD performance!")
        elif overall_avg < 500:
            print("⚠️  ACCEPTABLE performance")
        else:
            print("❌ POOR performance - needs optimization")
    
    print("\n🏁 Performance test completed!")

if __name__ == "__main__":
    main() 