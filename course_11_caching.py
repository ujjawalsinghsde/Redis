"""
COURSE 11: CACHING - Patterns & Strategies
===========================================

THEORY:
Caching speeds up applications by avoiding slow operations.
Multiple patterns for different use cases.

Patterns:

1. CACHE-ASIDE (Most Common)
   - Check cache, return if found
   - If miss, fetch from source
   - Update cache
   - Used for: databases, APIs

2. WRITE-THROUGH
   - Write to cache first
   - Then write to database
   - Ensures cache consistency
   - Used for: critical data

3. WRITE-BEHIND (Write-Back)
   - Write to cache immediately
   - Write to database later/async
   - Fast writes, eventual consistency
   - Used for: logs, analytics

4. REFRESH-AHEAD
   - Proactively refresh before expiry
   - Prevents cache misses
   - Good for popular data
   - Used for: trending, popular

Cache Invalidation Strategies:
  - TTL: Auto-expire
  - Event-based: Delete on change
  - Tags: Group related caches
  - Versioning: Create new key
"""

import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("CACHING - PATTERNS WITH UJJAWAL SINGH")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. CACHE-ASIDE Pattern
# ============================================================
print("1. CACHE-ASIDE - Most Common Pattern")
print("-" * 70)

def get_user_from_db(user_id):
    """Simulate database query"""
    print(f"  [DB] Querying database for {user_id}...")
    time.sleep(0.5)  # Simulate slowness
    return {"id": user_id, "name": "Ujjawal Singh", "email": "ujjawal@example.com"}

def get_user_cached(user_id):
    """Cache-aside pattern"""
    cache_key = f"user:{user_id}"

    # 1. Check cache
    cached = r.get(cache_key)
    if cached:
        print(f"  [CACHE HIT] Found in cache")
        return json.loads(cached)

    # 2. Cache miss - query database
    print(f"  [CACHE MISS] Not in cache")
    user_data = get_user_from_db(user_id)

    # 3. Store in cache (5 min TTL)
    r.setex(cache_key, 300, json.dumps(user_data))
    print(f"  [CACHE] Stored in cache (300s TTL)")

    return user_data

# First call - hits database
print("First request:")
start = time.time()
user1 = get_user_cached(user)
elapsed = time.time() - start
print(f"Time: {elapsed:.2f}s\n")

# Second call - hits cache
print("Second request (immediate):")
start = time.time()
user2 = get_user_cached(user)
elapsed = time.time() - start
print(f"Time: {elapsed:.4f}s (much faster!)\n")

# ============================================================
# 2. WRITE-THROUGH Pattern
# ============================================================
print("2. WRITE-THROUGH - Write Consistency")
print("-" * 70)

def update_user_write_through(user_id, data):
    """Write to cache, then database"""
    cache_key = f"user:{user_id}"

    # 1. Write to cache first
    r.set(cache_key, json.dumps(data))
    print(f"  [CACHE] Updated cache")

    # 2. Write to database
    print(f"  [DB] Writing to database...")
    time.sleep(0.2)  # Simulate DB write

    print(f"  [OK] Cache and DB are consistent")

print("Update user profile:")
updated_data = {
    "id": user,
    "name": "Ujjawal Singh",
    "email": "ujjawal.singh@example.com",
    "updated": True
}
update_user_write_through(user, updated_data)

# Verify
print(f"Cache contains: {r.get(f'user:{user}')}\n")

# ============================================================
# 3. Cache Invalidation - TTL
# ============================================================
print("3. CACHE INVALIDATION - TTL")
print("-" * 70)

cache_key = f"product:{user}:latest"
r.setex(cache_key, 60, json.dumps({"products": ["laptop", "phone"]}))

ttl = r.ttl(cache_key)
print(f"Cache set with {ttl}s TTL")
print(f"Automatically deleted after 60 seconds\n")

# ============================================================
# 4. Cache Invalidation - Event-Based
# ============================================================
print("4. CACHE INVALIDATION - Event-Based")
print("-" * 70)

# Cache exists
r.set(f"profile:{user}", json.dumps({"name": "Ujjawal"}))
print(f"Profile cached: {r.get(f'profile:{user}')}")

# User updates profile
print("User updates profile...")
r.delete(f"profile:{user}")  # Invalidate cache
print(f"Cache invalidated")

# Next request will miss cache
profile = r.get(f"profile:{user}")
print(f"Cache after update: {profile} (None = cache miss)\n")

# ============================================================
# 5. Cache Tags
# ============================================================
print("5. CACHE TAGS - Invalidate Related Caches")
print("-" * 70)

# Cache multiple things related to user
r.set(f"user:{user}:profile", "profile_data")
r.set(f"user:{user}:posts", "posts_data")
r.set(f"user:{user}:settings", "settings_data")

# Tag them for group invalidation
r.sadd(f"cache-tags:{user}", "profile", "posts", "settings")
print(f"Cached: profile, posts, settings")

# User deletes account - invalidate all related caches
print("User deletes account - invalidate all related caches")
tags = r.smembers(f"cache-tags:{user}")
for tag in tags:
    r.delete(f"user:{user}:{tag}")
print(f"All caches for {user} deleted\n")

# ============================================================
# 6. REAL-WORLD: Database Query Cache
# ============================================================
print("6. REAL-WORLD: Database Query Results")
print("-" * 70)

def get_top_posts(limit=10):
    """Get top posts with caching"""
    cache_key = "posts:top:10"

    # Check cache
    cached = r.get(cache_key)
    if cached:
        print(f"  [CACHE] Returning cached top posts")
        return json.loads(cached)

    # Query database (expensive)
    print(f"  [DB] Querying top {limit} posts...")
    time.sleep(0.3)

    posts = [
        {"id": 1, "title": "Redis Tips", "views": 5000},
        {"id": 2, "title": "Python Best Practices", "views": 3200},
    ]

    # Cache for 1 hour
    r.setex(cache_key, 3600, json.dumps(posts))
    return posts

# First call
print("Getting top posts (first call):")
posts = get_top_posts()
print(f"Got {len(posts)} posts\n")

# Second call
print("Getting top posts (second call):")
posts = get_top_posts()
print(f"Got {len(posts)} posts\n")

# ============================================================
# 7. REAL-WORLD: HTML Fragment Cache
# ============================================================
print("7. REAL-WORLD: Cache HTML Fragments")
print("-" * 70)

def render_header():
    """Render header (expensive)"""
    return "<header>Logo | Nav | Profile</header>"

def get_header_html():
    """Get header with caching"""
    cache_key = "html:header"

    cached = r.get(cache_key)
    if cached:
        print(f"  [CACHE] HTML header")
        return cached

    html = render_header()
    r.setex(cache_key, 3600, html)
    print(f"  [RENDER] Header rendered and cached")
    return html

print("Getting header:")
html = get_header_html()
print(f"Header: {html}\n")

# ============================================================
# 8. CACHE VERSIONING
# ============================================================
print("8. CACHE VERSIONING - Invalidate by Version")
print("-" * 70)

def get_config_v1():
    """Get config version 1"""
    config = {"feature_new": False, "limit": 100}
    r.set("config:v1", json.dumps(config))
    return config

def get_config_v2():
    """Get config version 2 (invalidates v1)"""
    config = {"feature_new": True, "limit": 200}
    r.set("config:v2", json.dumps(config))
    r.delete("config:v1")  # Invalidate old version
    return config

print("Version 1:")
config = get_config_v1()
print(f"  Feature new: {config['feature_new']}")

print("Version 2:")
config = get_config_v2()
print(f"  Feature new: {config['feature_new']}\n")

# ============================================================
# 9. CACHE METRICS
# ============================================================
print("9. CACHE METRICS - Monitor Performance")
print("-" * 70)

# Initialize metrics
r.set("cache:hits", 0)
r.set("cache:misses", 0)

# Simulate hits/misses
for i in range(10):
    if i % 3 == 0:
        r.incr("cache:misses")
    else:
        r.incr("cache:hits")

hits = int(r.get("cache:hits"))
misses = int(r.get("cache:misses"))
total = hits + misses
hit_rate = (hits / total * 100) if total > 0 else 0

print(f"Cache Hits: {hits}")
print(f"Cache Misses: {misses}")
print(f"Hit Rate: {hit_rate:.1f}%\n")

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("CACHING - PATTERNS SUMMARY")
print("="*70)
print("""
Cache-Aside (Most Used):
  1. Check cache
  2. If miss, query source
  3. Update cache
  Used for: Read-heavy workloads

Write-Through:
  1. Write to cache
  2. Write to database
  Used for: Consistency critical

Write-Behind:
  1. Write to cache (return immediately)
  2. Async write to database
  Used for: High performance, eventual consistency

Invalidation Strategies:
  TTL: Automatic expiration
  Event-Based: Delete on change
  Tags: Group invalidation
  Versioning: New key version

Tips:
  [OK] Choose TTL based on data freshness
  [OK] Monitor cache hit rate
  [OK] Size cache appropriately
  [OK] Invalidate on updates
  [OK] Handle cache misses
  [OK] Use consistent keys
  [OK] Test cache behavior

Anti-Patterns:
  [NO] Cache everything
  [NO] Infinite TTL without invalidation
  [NO] Ignore cache consistency
  [NO] Cache confidential data unsecured
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Implement cache-aside for user data
2. Build write-through for consistency
3. Create cache invalidation on update
4. Implement cache tags
5. Build cache versioning system
6. Create cache metrics tracking
7. Implement multi-level cache
8. Build cache warming system
9. Create cache garbage collection
10. Implement cache preview system

Modify the code and experiment!
""")
