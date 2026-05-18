"""
COURSE 2: STRINGS - The Most Common Data Type
==============================================

THEORY:
Strings in Redis are the most versatile data type.
They can store:
  - Regular text
  - Numbers
  - JSON
  - Binary data
  - Anything!

Common String Operations:

1. SET / GET
   SET key value           - Store value
   GET key                 - Retrieve value

2. APPEND
   APPEND key value        - Add to end of string

3. STRLEN
   STRLEN key              - Get length

4. INCR / DECR
   INCR key                - Increment number by 1
   DECR key                - Decrement number by 1
   INCRBY key amount       - Increment by amount
   DECRBY key amount       - Decrement by amount

5. GETRANGE / SETRANGE
   GETRANGE key start end  - Get substring
   SETRANGE key offset val - Replace part of string

6. SETEX / PSETEX
   SETEX key seconds val   - Set with expiration
   PSETEX key millis val   - Set with ms expiration

7. MSET / MGET
   MSET k1 v1 k2 v2       - Set multiple
   MGET k1 k2 k3          - Get multiple

8. GETSET
   GETSET key value        - Set new, return old

9. SETNX
   SETNX key value         - Set only if not exists

Performance:
  - All string operations O(1) or O(N) where N = string length
  - Very fast!

Use Cases for Strings:
  - Counters (views, likes, followers)
  - Caches (HTML, JSON, user data)
  - Sessions
  - Authentication tokens
  - Rate limiting counters
  - Leaderboard scores

"""

import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("STRING OPERATIONS WITH UJJAWAL SINGH'S PROFILE")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. BASIC SET & GET
# ============================================================
print("1. BASIC SET & GET")
print("-" * 70)

r.set(f"{user}:name", "Ujjawal Singh")
r.set(f"{user}:title", "Software Engineer")
r.set(f"{user}:bio", "Learning Redis and building awesome apps")

print(f"Name: {r.get(f'{user}:name')}")
print(f"Title: {r.get(f'{user}:title')}")
print(f"Bio: {r.get(f'{user}:bio')}\n")

# ============================================================
# 2. MSET & MGET - Store Multiple at Once
# ============================================================
print("2. MSET & MGET - Store Multiple Keys")
print("-" * 70)

# Store multiple profile fields at once (faster!)
r.mset({
    f"{user}:email": "ujjawal@example.com",
    f"{user}:location": "India",
    f"{user}:country": "India",
    f"{user}:timezone": "IST"
})

# Retrieve multiple keys at once
keys = [
    f"{user}:email",
    f"{user}:location",
    f"{user}:country"
]
values = r.mget(keys)

for key, value in zip(keys, values):
    print(f"{key.split(':')[1]}: {value}")
print()

# ============================================================
# 3. SETEX - Set with Expiration
# ============================================================
print("3. SETEX - Temporary Data (Auto-Expire)")
print("-" * 70)

# Store temporary login session (expires in 1 hour)
session_token = "abc123xyz789"
r.setex(
    f"{user}:session",
    3600,  # 1 hour in seconds
    session_token
)

ttl = r.ttl(f"{user}:session")
print(f"Session token: {session_token}")
print(f"TTL (expires in): {ttl} seconds")
print(f"That's {ttl // 60} minutes\n")

# ============================================================
# 4. INCR & DECR - Counters
# ============================================================
print("4. INCR / DECR - Tracking Counters")
print("-" * 70)

# Initialize counters
r.set(f"{user}:followers", 100)
r.set(f"{user}:posts", 25)
r.set(f"{user}:likes", 500)

print("Initial state:")
print(f"  Followers: {r.get(f'{user}:followers')}")
print(f"  Posts: {r.get(f'{user}:posts')}")
print(f"  Likes: {r.get(f'{user}:likes')}\n")

# Someone follows him
r.incr(f"{user}:followers")
print("After someone followed:")
print(f"  Followers: {r.get(f'{user}:followers')}\n")

# He made a new post
r.incr(f"{user}:posts")
print("After new post:")
print(f"  Posts: {r.get(f'{user}:posts')}\n")

# Received 15 likes on a post
r.incrby(f"{user}:likes", 15)
print("After 15 likes:")
print(f"  Likes: {r.get(f'{user}:likes')}\n")

# ============================================================
# 5. APPEND - Add to String
# ============================================================
print("5. APPEND - Adding to Strings")
print("-" * 70)

r.set(f"{user}:bio", "Engineer")
print(f"Initial bio: {r.get(f'{user}:bio')}")

r.append(f"{user}:bio", " | Python Developer")
print(f"After append: {r.get(f'{user}:bio')}\n")

# ============================================================
# 6. STRLEN - Get Length
# ============================================================
print("6. STRLEN - String Length")
print("-" * 70)

bio = r.get(f"{user}:bio")
length = r.strlen(f"{user}:bio")
print(f"Bio: {bio}")
print(f"Length: {length} characters\n")

# ============================================================
# 7. GETRANGE - Get Part of String
# ============================================================
print("7. GETRANGE - Extract Substring")
print("-" * 70)

bio = r.get(f"{user}:bio")
print(f"Full bio: {bio}")

# Get first 8 characters
part1 = r.getrange(f"{user}:bio", 0, 7)
print(f"First 8 chars: {part1}")

# Get last 10 characters
part2 = r.getrange(f"{user}:bio", -10, -1)
print(f"Last 10 chars: {part2}\n")

# ============================================================
# 8. SETRANGE - Replace Part of String
# ============================================================
print("8. SETRANGE - Replace Part of String")
print("-" * 70)

r.set(f"{user}:status", "I am learning Redis!")
print(f"Original: {r.get(f'{user}:status')}")

r.setrange(f"{user}:status", 10, "MASTERING")
print(f"After replace: {r.get(f'{user}:status')}\n")

# ============================================================
# 9. SETNX - Set Only if Not Exists
# ============================================================
print("9. SETNX - Set Only if Key Doesn't Exist")
print("-" * 70)

# First time - will be set (returns 1)
result1 = r.setnx(f"{user}:favorite-color", "blue")
print(f"SETNX for new key: {result1} (1 = set successfully)")

# Second time - won't be set (returns 0)
result2 = r.setnx(f"{user}:favorite-color", "red")
print(f"SETNX for existing key: {result2} (0 = not set, already exists)")
print(f"Value is still: {r.get(f'{user}:favorite-color')}\n")

# ============================================================
# 10. GETSET - Set New & Get Old
# ============================================================
print("10. GETSET - Atomic Get & Set")
print("-" * 70)

r.set(f"{user}:status", "online")
print(f"Current status: {r.get(f'{user}:status')}")

old_value = r.getset(f"{user}:status", "away")
print(f"Old value: {old_value}")
print(f"New value: {r.get(f'{user}:status')}\n")

# ============================================================
# 11. JSON STORAGE - Real-World Example
# ============================================================
print("11. STORING COMPLEX DATA (JSON)")
print("-" * 70)

# Store complete profile as JSON
profile = {
    'name': 'Ujjawal Singh',
    'age': 25,
    'skills': ['Python', 'Redis', 'JavaScript'],
    'experience_years': 3,
    'company': 'Tech Startup',
    'remote': True
}

r.set(
    f"{user}:profile",
    json.dumps(profile)  # Convert to JSON string
)

# Retrieve and parse
stored_json = r.get(f"{user}:profile")
parsed_profile = json.loads(stored_json)

print(f"Stored profile:")
for key, value in parsed_profile.items():
    print(f"  {key}: {value}\n")

# ============================================================
# 12. PRACTICAL PATTERN - Page View Counter
# ============================================================
print("12. REAL-WORLD: Page View Counter")
print("-" * 70)

# Simulate website traffic
page_key = "page:profile:ujjawal-singh:views"
r.set(page_key, 0)

print("Simulating page views...")
for day in range(1, 6):
    views_today = day * 50  # 50 views/day increasing
    r.incrby(page_key, views_today)
    print(f"  Day {day}: +{views_today} views, Total: {r.get(page_key)}")

print(f"\nTotal page views: {r.get(page_key)}\n")

# ============================================================
# 13. PRACTICAL PATTERN - Rate Limiting
# ============================================================
print("13. REAL-WORLD: Rate Limiting")
print("-" * 70)

def check_rate_limit(user_id, limit=10, window=60):
    """
    Check if user exceeded API limit
    limit = max requests
    window = time window in seconds
    """
    key = f"rate:{user_id}"
    current = r.get(key)

    if current is None:
        # First request
        r.setex(key, window, 1)
        return True, 1

    current_count = int(current)
    if current_count >= limit:
        # Exceeded limit
        return False, current_count
    else:
        # Allow and increment
        r.incr(key)
        return True, current_count + 1

# Simulate API calls
print("Simulating API requests...")
for i in range(12):
    allowed, count = check_rate_limit(user, limit=10)
    status = "ALLOWED" if allowed else "BLOCKED"
    print(f"  Request {i+1}: {status} (count: {count}/10)")

print()

# ============================================================
# 14. PRACTICAL PATTERN - Distributed Lock
# ============================================================
print("14. REAL-WORLD: Distributed Lock")
print("-" * 70)

def acquire_lock(resource, timeout=10):
    """Acquire a lock for a resource"""
    lock_key = f"lock:{resource}"
    # SETNX returns 1 if set, 0 if already exists
    acquired = r.setnx(lock_key, "locked")
    if acquired:
        r.expire(lock_key, timeout)
    return acquired

def release_lock(resource):
    """Release a lock"""
    lock_key = f"lock:{resource}"
    r.delete(lock_key)

# Try to acquire lock
resource = "critical-task"
print(f"Trying to acquire lock for '{resource}'...")

if acquire_lock(resource):
    print("Lock acquired! Doing critical work...")
    # Do something critical
    print("Work completed")
    release_lock(resource)
    print("Lock released\n")
else:
    print("Another process already has the lock!\n")

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("STRINGS - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Basic:
  SET key value               - Store value
  GET key                     - Retrieve value
  MSET k1 v1 k2 v2           - Set multiple
  MGET k1 k2 k3              - Get multiple

Numbers:
  INCR key                    - Increment by 1
  DECR key                    - Decrement by 1
  INCRBY key 5                - Increment by 5
  DECRBY key 3                - Decrement by 3

Manipulation:
  APPEND key value            - Add to end
  STRLEN key                  - Get length
  GETRANGE key 0 5            - Get substring
  SETRANGE key 0 value        - Replace part

Expiration:
  SETEX key 60 value          - Set with expiration
  PSETEX key 5000 value       - Set with ms expiration

Conditions:
  SETNX key value             - Set only if not exists
  GETSET key value            - Get old, set new

Use Cases:
  [OK] Counters (likes, views, followers)
  [OK] Caches (JSON objects, HTML)
  [OK] Sessions & tokens
  [OK] Rate limiting
  [OK] Locks
  [OK] Temporary data
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Store Ujjawal Singh's programming languages with MSET
2. Create a post view counter and increment it 100 times
3. Store a JSON object with user preferences, retrieve and parse it
4. Implement a simple login session with 30-minute expiration
5. Create a rate limiter that allows 5 requests per minute
6. Store your GitHub profile as JSON and display it
7. Create a distributed lock for a database migration

Modify the code and experiment!
""")

# ============================================================
# PRACTICE: Solutions
# ============================================================
print("="*70)
print("PRACTICE: Solutions")
print("="*70 + "\n")

# Task 1: Store Ujjawal Singh's programming languages with MSET
print("1. Store Programming Languages with MSET")
print("-" * 70)

languages = {
    f"{user}:lang:1": "Python",
    f"{user}:lang:2": "Java",
    f"{user}:lang:3": "Go",
    f"{user}:lang:4": "C++"
}
r.mset(languages)

lang_keys = [f"{user}:lang:1", f"{user}:lang:2", f"{user}:lang:3", f"{user}:lang:4"]
langs = r.mget(lang_keys)
print(f"Languages stored: {', '.join(langs)}\n")

# Task 2: Create a post view counter and increment it 100 times
print("2. Post View Counter - Increment 100 Times")
print("-" * 70)

post_views_key = f"{user}:post:1:views"
r.set(post_views_key, 0)

for i in range(1, 101):
    r.incr(post_views_key)

total_views = r.get(post_views_key)
print(f"Total views after 100 increments: {total_views}")
print(f"Final counter value: {r.get(post_views_key)}\n")

# Task 3: Store a JSON object with user preferences, retrieve and parse it
print("3. Store & Parse JSON - User Preferences")
print("-" * 70)

preferences = {
    'theme': 'dark',
    'notifications': True,
    'language': 'en',
    'privacy': 'public',
    'email_updates': False
}

r.set(f"{user}:preferences", json.dumps(preferences))
stored = json.loads(r.get(f"{user}:preferences"))

print("Stored preferences:")
for key, value in stored.items():
    print(f"  {key}: {value}\n")

# Task 4: Implement a simple login session with 30-minute expiration
print("4. Login Session with 30-Minute Expiration")
print("-" * 70)

session_id = "sess_user_ujjawal_12345"
expiry_seconds = 30 * 60  # 30 minutes

r.setex(f"{user}:session:{session_id}", expiry_seconds, json.dumps({
    'user_id': user,
    'login_time': '2026-05-18 10:30:00',
    'ip_address': '192.168.1.1'
}))

session_ttl = r.ttl(f"{user}:session:{session_id}")
print(f"Session ID: {session_id}")
print(f"TTL: {session_ttl} seconds ({session_ttl // 60} minutes)")
print(f"Session data: {r.get(f'{user}:session:{session_id}')}\n")

# Task 5: Create a rate limiter that allows 5 requests per minute
print("5. Rate Limiter - 5 Requests per Minute")
print("-" * 70)

def rate_limit_5_per_min(user_id, limit=5, window=60):
    """Allow 5 requests per minute"""
    key = f"rate:{user_id}:minute"
    current = r.get(key)
    
    if current is None:
        r.setex(key, window, 1)
        return True, 1
    
    current_count = int(current)
    if current_count >= limit:
        return False, current_count
    else:
        r.incr(key)
        return True, current_count + 1

print("Testing rate limiter (allowing 5 per minute)...")
for i in range(8):
    allowed, count = rate_limit_5_per_min(user, limit=5)
    status = "[OK] ALLOWED" if allowed else "[BLOCKED]"
    print(f"  Request {i+1}: {status} ({count}/5)")
print()

# Task 6: Store your GitHub profile as JSON and display it
print("6. Store & Display GitHub Profile (JSON)")
print("-" * 70)

github_profile = {
    'username': 'ujjawal-singh',
    'name': 'Ujjawal Singh',
    'bio': 'Redis Enthusiast | Software Engineer',
    'followers': 234,
    'following': 120,
    'public_repos': 45,
    'company': 'Tech Startup',
    'location': 'India',
    'blog': 'blog.ujjawal.dev',
    'twitter': '@ujjawalsinghsde',
    'skills': ['Python', 'Redis', 'Java', 'Go']
}

r.set(f"{user}:github-profile", json.dumps(github_profile))
profile_data = json.loads(r.get(f"{user}:github-profile"))

print("GitHub Profile:")
for key, value in profile_data.items():
    print(f"  {key}: {value}\n")

# Task 7: Create a distributed lock for a database migration
print("7. Distributed Lock - Database Migration")
print("-" * 70)

def acquire_migration_lock(migration_name, timeout=300):
    """Acquire lock for database migration (5 minutes)"""
    lock_key = f"migration:lock:{migration_name}"
    acquired = r.setnx(lock_key, json.dumps({
        'started': '2026-05-18 10:30:00',
        'process_id': 'process_123'
    }))
    if acquired:
        r.expire(lock_key, timeout)
        return True
    return False

def release_migration_lock(migration_name):
    """Release migration lock"""
    lock_key = f"migration:lock:{migration_name}"
    r.delete(lock_key)

# Simulate migration
migration = "add_indexes_to_users_table"
print(f"Attempting to acquire lock for migration: {migration}")

if acquire_migration_lock(migration):
    print("[OK] Lock acquired! Running migration...")
    lock_key = f"migration:lock:{migration}"
    print(f"  Lock data: {r.get(lock_key)}")
    print("  [Simulating migration execution...]")
    print("[OK] Migration completed")
    release_migration_lock(migration)
    print("[OK] Lock released\n")
else:
    print("[BLOCKED] Another process already running this migration!\n")

print("="*70)
print("ALL PRACTICE PROBLEMS COMPLETED!")
print("="*70)
