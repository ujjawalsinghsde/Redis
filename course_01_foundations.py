"""
COURSE 1: FOUNDATIONS - What is Redis & Why Use It
====================================================

THEORY:
1. What is Redis?
   - Remote Dictionary Server
   - In-memory data store (fast!)
   - Key-value database
   - Can persist to disk
   - Single-threaded (but fast!)

2. Why Redis?
   - Speed: 100,000+ operations per second
   - Memory-efficient: optimized data structures
   - Versatile: many data types
   - Atomic: operations are atomic
   - Expiration: automatic key deletion

3. Comparison with Other DBs:

   | Feature        | Redis | PostgreSQL | MongoDB |
   |----------------|-------|-----------|---------|
   | Speed          | FAST  | Slow      | Medium  |
   | Type           | Cache | SQL DB    | NoSQL   |
   | Persistence    | Yes   | Yes       | Yes     |
   | Memory use     | High  | Low       | Medium  |
   | Complex queries| No    | Yes       | Yes     |

4. When to Use Redis:
   [OK] Caching layer (cache everything!)
   [OK] Sessions storage
   [OK] Real-time analytics
   [OK] Leaderboards & rankings
   [OK] Message queues
   [OK] Rate limiting
   [OK] Chat & notifications
   [NO] Large file storage
   [NO] Complex relational queries
   [NO] ACID transactions (Redis has limited transactions)

5. Redis Limitations:
   - All data in memory (limited by RAM)
   - Not suitable for large files
   - Single-threaded (can be bottleneck)
   - No complex queries (no WHERE, JOIN, etc)
   - Data is lost if server crashes (unless persisted)

6. Use Cases:
   A) Ujjawal Singh's Social Media App:
      [OK] User sessions: store login info
      [OK] Cache: cache user profiles
      [OK] Notifications: pub/sub for new messages
      [OK] Leaderboards: top users by followers
      [OK] Activity feed: recent posts by friends

   B) E-commerce Site:
      [OK] Product cache: cache frequently viewed products
      [OK] Shopping cart: store cart items temporarily
      [OK] Inventory: track stock levels (with TTL)
      [OK] Recommendations: cache recommendations
      [OK] Rate limiting: limit API calls per user

7. Architecture:
   Client (Python) ---> Redis Server (port 6379) ---> Memory
                             |
                          Disk (optional)

"""

import redis
import time
from datetime import datetime

# Connection Setup
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Clear for fresh start
r.flushdb()

print(__doc__)

print("\n" + "="*60)
print("PRACTICAL EXAMPLE: Ujjawal Singh's Social Media App")
print("="*60 + "\n")

# ============================================================
# EXAMPLE 1: Basic Setup for User
# ============================================================
print("EXAMPLE 1: Basic User Setup")
print("-" * 60)

# Let's create Ujjawal Singh's account
user_id = "ujjawal-singh"

# Store basic info (we'll use STRINGS for now)
r.set(f"{user_id}:name", "Ujjawal Singh")
r.set(f"{user_id}:email", "ujjawal@example.com")
r.set(f"{user_id}:followers", 150)
r.set(f"{user_id}:following", 200)

print(f"Created user: {user_id}")
print(f"Name: {r.get(f'{user_id}:name')}")
print(f"Email: {r.get(f'{user_id}:email')}")
print(f"Followers: {r.get(f'{user_id}:followers')}")
print()

# ============================================================
# EXAMPLE 2: Performance Comparison
# ============================================================
print("EXAMPLE 2: Why Redis is Fast")
print("-" * 60)

# Simulate slow operation (database query)
def slow_get_profile():
    """Simulates 100ms database query"""
    time.sleep(0.1)
    return {
        'name': 'Ujjawal Singh',
        'bio': 'Developer | Learning Redis',
        'location': 'India'
    }

# First time - slow (from database)
print("First request (from database):")
start = time.time()
profile = slow_get_profile()
elapsed = time.time() - start
print(f"  Time: {elapsed*1000:.2f}ms")
print(f"  Data: {profile}")

# Cache it in Redis
import json
cache_key = f"{user_id}:profile"
r.set(cache_key, json.dumps(profile))

# Second time - fast (from Redis cache)
print("\nSecond request (from Redis cache):")
start = time.time()
cached_profile = json.loads(r.get(cache_key))
elapsed = time.time() - start
print(f"  Time: {elapsed*1000:.4f}ms")  # Should be < 1ms
print(f"  Data: {cached_profile}")

speedup = 100  # Approximately 100x faster
print(f"\n  >>> Speedup: ~{speedup}x faster! <<<")
print()

# ============================================================
# EXAMPLE 3: Key Concepts
# ============================================================
print("EXAMPLE 3: Redis Key Concepts")
print("-" * 60)

# Concept 1: Keys and Values
print("1. Keys and Values:")
print("   - Keys are strings (like variable names)")
print("   - Values can be different types")

keys = [
    f"{user_id}:name",
    f"{user_id}:followers",
    f"{user_id}:profile",
]
print(f"   Keys in Redis: {keys}")
print()

# Concept 2: Expiration
print("2. Automatic Expiration (TTL):")
temp_token = f"{user_id}:session:abc123"
r.setex(temp_token, 3600, "session_data_here")  # Expires in 1 hour
ttl = r.ttl(temp_token)
print(f"   Set token: {temp_token}")
print(f"   TTL: {ttl} seconds (auto-delete in {ttl//60} minutes)")
print()

# Concept 3: Multiple Data Types
print("3. Different Data Types:")
r.set(f"{user_id}:age", 25)  # String (number)
r.lpush(f"{user_id}:posts", "post1")  # List
r.sadd(f"{user_id}:tags", "python")  # Set
r.hset(f"{user_id}:settings", mapping={'theme': 'dark'})  # Hash

types = {
    f"{user_id}:age": r.type(f"{user_id}:age"),
    f"{user_id}:posts": r.type(f"{user_id}:posts"),
    f"{user_id}:tags": r.type(f"{user_id}:tags"),
    f"{user_id}:settings": r.type(f"{user_id}:settings"),
}
for key, key_type in types.items():
    print(f"   {key} -> {key_type}")
print()

# Concept 4: Atomic Operations
print("4. Atomic Operations (no race conditions):")
print("   Redis operations are atomic (not interrupted)")
r.set(f"{user_id}:likes", 0)
for i in range(5):
    r.incr(f"{user_id}:likes")  # Atomically increment
likes = r.get(f"{user_id}:likes")
print(f"   {user_id} received {likes} likes (5 increments)")
print()

# ============================================================
# EXAMPLE 4: Real Use Case
# ============================================================
print("EXAMPLE 4: Real-World Scenario")
print("-" * 60)
print("Scenario: User posts a tweet\n")

# Step 1: User creates a post
post_id = "post:001"
r.hset(f"{user_id}:my-posts", mapping={
    post_id: json.dumps({
        'content': 'Just learned Redis!',
        'timestamp': str(datetime.now()),
        'likes': 0
    })
})
print("1. Post created")

# Step 2: Store in feed (list of recent posts)
feed_key = f"{user_id}:my-feed"
r.lpush(feed_key, post_id)
print("2. Post added to feed")

# Step 3: Cache the post (expires after 1 hour)
r.setex(f"cache:post:{post_id}", 3600, json.dumps({
    'author': user_id,
    'content': 'Just learned Redis!'
}))
print("3. Post cached for fast retrieval")

# Step 4: Add to search index (set for tags)
r.sadd("search:redis", post_id)
print("4. Post indexed for search")

# Step 5: Retrieve and display
feed_posts = r.lrange(f"{user_id}:my-feed", 0, -1)
print(f"5. Retrieved from feed: {feed_posts}")
print()

# ============================================================
# SUMMARY
# ============================================================
print("="*60)
print("KEY TAKEAWAYS")
print("="*60)
print("""
1. Redis is fast in-memory database
2. Perfect for caching and sessions
3. Supports multiple data types
4. Operations are atomic (thread-safe)
5. Keys can auto-expire (TTL)
6. Not suitable for large files
7. Data is in memory (limited by RAM)

Next: Learn all 5 main data types!
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*60)
print("PRACTICE: Try These!")
print("="*60)
print("""
1. Store Ujjawal Singh's followers in Redis with TTL of 24 hours
2. Set an age that auto-expires in 60 seconds, check TTL
3. Create a cache key that stores a JSON object
4. Check what types Redis has for your stored keys
5. Create 3 different data types in Redis

Modify the code above and run it!
""")
