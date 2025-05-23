#!/usr/bin/env python3
"""
Cache management script for manual cache clearing and monitoring.
"""

import sys
import os
sys.path.insert(0, '.')

def clear_cache():
    """Clear the application cache."""
    try:
        from app import _cache, _cache_timeout
        cache_count = len(_cache)
        _cache.clear()
        _cache_timeout.clear()
        print(f"✅ Cleared {cache_count} cached entries")
        return True
    except Exception as e:
        print(f"❌ Error clearing cache: {str(e)}")
        return False

def show_cache_stats():
    """Show current cache statistics."""
    try:
        from app import _cache, _cache_timeout
        from datetime import datetime
        
        cache_count = len(_cache)
        timeout_count = len(_cache_timeout)
        
        print(f"📊 Cache Statistics:")
        print(f"  Total cached entries: {cache_count}")
        print(f"  Timeout entries: {timeout_count}")
        
        if cache_count > 0:
            # Show cache keys and their approximate sizes
            total_size = 0
            now = datetime.utcnow().timestamp()
            active_count = 0
            
            print(f"\n📋 Cached Routes:")
            for key, value in _cache.items():
                try:
                    size = len(str(value))
                    total_size += size
                    
                    # Check if still valid
                    is_valid = key in _cache_timeout and now < _cache_timeout[key]
                    status = "🟢 Active" if is_valid else "🔴 Expired"
                    
                    if is_valid:
                        active_count += 1
                    
                    print(f"  {status} {key[:50]:<50} ({size:,} bytes)")
                except:
                    print(f"  ❓ {key[:50]:<50} (unknown size)")
            
            print(f"\n📈 Summary:")
            print(f"  Active entries: {active_count}/{cache_count}")
            print(f"  Estimated total size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
        
        return True
    except Exception as e:
        print(f"❌ Error getting cache stats: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("🗄️ Cache Management Tool")
        print("Usage:")
        print("  python clear_cache.py stats    - Show cache statistics")
        print("  python clear_cache.py clear    - Clear all cache")
        print("  python clear_cache.py restart  - Clear cache and show stats")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        print("🗄️ Cache Statistics")
        print("=" * 50)
        show_cache_stats()
        
    elif command == "clear":
        print("🗄️ Clearing Cache")
        print("=" * 50)
        if clear_cache():
            print("✅ Cache cleared successfully!")
        else:
            print("❌ Failed to clear cache")
            
    elif command == "restart":
        print("🗄️ Cache Restart")
        print("=" * 50)
        print("Before clearing:")
        show_cache_stats()
        print("\nClearing cache...")
        if clear_cache():
            print("\nAfter clearing:")
            show_cache_stats()
        else:
            print("❌ Failed to restart cache")
            
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: stats, clear, restart")

if __name__ == "__main__":
    main() 