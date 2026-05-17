"""
COURSE 7: EXPIRATION & TTL - Auto-Expiring Keys
=================================================

THEORY:
Keys can automatically expire (delete) after a time.
Perfect for temporary data like sessions, caches, OTPs.

Key Concepts:
  - TTL = Time To Live (in seconds)
  - Keys auto-deleted after TTL
  - Can check remaining time
  - Useful for temporary data
  - Reduces manual cleanup

Common Operations:

1. EXPIRE - Set Expiration (seconds)
   EXPIRE key seconds

2. EXPIREAT - Expire at Unix Timestamp
   EXPIREAT key timestamp

3. PEXPIRE - Expire in Milliseconds
   PEXPIRE key milliseconds

4. TTL - Get Time to Live
   TTL key (returns -1 if no expiration, -2 if not exist)

5. PTTL - Get TTL in Milliseconds
   PTTL key

6. PERSIST - Remove Expiration
   PERSIST key (make it permanent)

7. SETEX - Set with Expiration (Strings)
   SETEX key seconds value

8. PSETEX - Set with Expiration (milliseconds)
   PSETEX key milliseconds value

Expiration Policies:
  - LRU: Evict least recently used
  - LFU: Evict least frequently used
  - Random: Random eviction
  - TTL: Evict soon-to-expire keys

Performance:
  - EXPIRE, TTL: O(1)
  - Background cleanup (not exact timing)
  - Can be 1-2 seconds off
"""

import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("EXPIRATION - TTL WITH UJJAWAL SINGH")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. SETEX - Set with Expiration
# ============================================================
print("1. SETEX - Set Data with Auto-Expiration")
print("-" * 70)

# Store temporary authentication token (5 seconds for demo)
r.setex(f"{user}:auth-token", 5, "abc123xyz")
print(f"Set auth token (expires in 5 seconds)")

ttl = r.ttl(f"{user}:auth-token")
print(f"TTL: {ttl} seconds")

# Token is valid
token = r.get(f"{user}:auth-token")
print(f"Token exists: {token}\n")

# ============================================================
# 2. EXPIRE - Add Expiration to Existing Key
# ============================================================
print("2. EXPIRE - Add Expiration to Existing Key")
print("-" * 70)

r.set(f"{user}:cache-key", "some data")
print("Set cache key (no expiration)")

r.expire(f"{user}:cache-key", 60)
print("Added 60 second expiration")

ttl = r.ttl(f"{user}:cache-key")
print(f"TTL: {ttl} seconds\n")

# ============================================================
# 3. TTL - Check Time Remaining
# ============================================================
print("3. TTL - Check Time Remaining")
print("-" * 70)

# Key with expiration
ttl = r.ttl(f"{user}:cache-key")
print(f"Cache key TTL: {ttl} seconds")

# Key without expiration
r.set(f"{user}:permanent-key", "never expires")
ttl = r.ttl(f"{user}:permanent-key")
print(f"Permanent key TTL: {ttl} (-1 means no expiration)")

# Non-existent key
ttl = r.ttl("nonexistent-key")
print(f"Non-existent key TTL: {ttl} (-2 means doesn't exist)\n")

# ============================================================
# 4. PERSIST - Remove Expiration
# ============================================================
print("4. PERSIST - Make Key Permanent")
print("-" * 70)

key = f"{user}:temp-data"
r.setex(key, 60, "temporary")
print(f"TTL before persist: {r.ttl(key)} seconds")

r.persist(key)
print(f"TTL after persist: {r.ttl(key)} (-1 = permanent)")
print(f"Key still exists: {r.get(key)}\n")

# ============================================================
# 5. PEXPIRE - Millisecond Precision
# ============================================================
print("5. PEXPIRE - Expiration in Milliseconds")
print("-" * 70)

r.set(f"{user}:precise-timing", "data")
r.pexpire(f"{user}:precise-timing", 5000)  # 5 seconds

pttl = r.pttl(f"{user}:precise-timing")
print(f"PTTL (milliseconds): {pttl} ms\n")

# ============================================================
# 6. REAL-WORLD: Session Management
# ============================================================
print("6. REAL-WORLD: Session Management")
print("-" * 70)

session_key = f"{user}:session:xyz789"
r.hset(session_key, mapping={
    "user_id": user,
    "logged_in_at": str(time.time()),
    "ip": "203.0.113.5"
})

# Session expires in 30 minutes
r.expire(session_key, 30 * 60)
ttl = r.ttl(session_key)
print(f"Session created")
print(f"Expires in: {ttl // 60} minutes ({ttl} seconds)")
print(f"Session data: {r.hgetall(session_key)}\n")

# ============================================================
# 7. REAL-WORLD: OTP (One-Time Password)
# ============================================================
print("7. REAL-WORLD: One-Time Password (OTP)")
print("-" * 70)

otp_code = "634827"
otp_key = f"{user}:otp:email-verification"

# OTP expires in 10 minutes
r.setex(otp_key, 10 * 60, otp_code)
print(f"OTP sent: {otp_code}")
print(f"Expires in: 10 minutes")

ttl = r.ttl(otp_key)
print(f"TTL: {ttl} seconds")

# Verify OTP before expiration
stored_otp = r.get(otp_key)
if stored_otp == otp_code:
    print(f"OTP verification: SUCCESSFUL\n")

# ============================================================
# 8. REAL-WORLD: Cache with TTL
# ============================================================
print("8. REAL-WORLD: Database Query Cache")
print("-" * 70)

# Simulate expensive query
def get_user_expensive():
    print("  [SLOW] Querying database...")
    time.sleep(0.5)
    return {"name": "Ujjawal", "age": 25}

cache_key = f"cache:user:{user}"

# Check cache
cached = r.get(cache_key)
if cached is None:
    print("Cache miss - fetching from database")
    user_data = get_user_expensive()
    import json
    r.setex(cache_key, 300, json.dumps(user_data))  # Cache for 5 min
    print(f"Cached for 5 minutes")
else:
    print("Cache hit!")

print(f"TTL: {r.ttl(cache_key)} seconds\n")

# ============================================================
# 9. REAL-WORLD: Rate Limiting (Sliding Window)
# ============================================================
print("9. REAL-WORLD: Rate Limiting")
print("-" * 70)

def check_rate_limit(ip, limit=5, window=60):
    key = f"rate:{ip}"
    count = r.incr(key)

    if count == 1:
        # First request in window
        r.expire(key, window)

    if count > limit:
        ttl = r.ttl(key)
        return False, ttl

    return True, count

# Simulate API requests
print("Simulating API requests...")
for i in range(7):
    allowed, info = check_rate_limit("203.0.113.5", limit=5, window=60)
    if allowed:
        print(f"  Request {i+1}: ALLOWED (count: {info})")
    else:
        print(f"  Request {i+1}: BLOCKED (reset in {info} seconds)")
print()

# ============================================================
# 10. REAL-WORLD: Cleanup Old Data
# ============================================================
print("10. REAL-WORLD: Automatic Cleanup")
print("-" * 70)

# Add temporary log entries
r.lpush("logs:errors", "Error 1", "Error 2", "Error 3")
r.expire("logs:errors", 3600)  # Keep for 1 hour

print(f"Error log created")
print(f"Auto-deletes in: {r.ttl('logs:errors')} seconds (1 hour)")
print(f"Errors: {r.lrange('logs:errors', 0, -1)}\n")

# ============================================================
# 11. REAL-WORLD: Temporary Feature Flag
# ============================================================
print("11. REAL-WORLD: Temporary Feature Flag")
print("-" * 70)

# Feature enabled for testing (30 minutes)
r.setex("feature:new-dashboard", 30 * 60, "enabled")

feature_ttl = r.ttl("feature:new-dashboard")
if feature_ttl > 0:
    print(f"New dashboard feature: ENABLED (for {feature_ttl // 60} more minutes)")
else:
    print(f"New dashboard feature: DISABLED")
print()

# ============================================================
# 12. EXPIREAT - Expire at Specific Time
# ============================================================
print("12. EXPIREAT - Expire at Specific Unix Timestamp")
print("-" * 70)

future_timestamp = int(time.time()) + 120  # 2 minutes from now
key = f"{user}:future-expiry"

r.set(key, "data")
r.expireat(key, future_timestamp)

ttl = r.ttl(key)
print(f"Key set to expire at Unix timestamp: {future_timestamp}")
print(f"TTL: {ttl} seconds\n")

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("EXPIRATION - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Set with Expiration:
  SETEX key seconds value      - Set + expire (seconds)
  PSETEX key ms value          - Set + expire (milliseconds)
  HSET key field value + EXPIRE - Hash + expire

Add Expiration:
  EXPIRE key seconds           - Set expiration (seconds)
  PEXPIRE key milliseconds     - Set expiration (milliseconds)
  EXPIREAT key timestamp       - Expire at Unix timestamp

Query:
  TTL key                      - Get seconds until expiration
  PTTL key                     - Get milliseconds until expiration
  (-1 = no expiration, -2 = doesn't exist)

Remove Expiration:
  PERSIST key                  - Make key permanent

Use Cases:
  [OK] Session management
  [OK] OTP (one-time passwords)
  [OK] Caching (auto-invalidate)
  [OK] Rate limiting
  [OK] Temporary locks
  [OK] Feature flags
  [OK] Email verification
  [OK] Password reset tokens
  [OK] Auto-cleanup old data

Common TTL Values:
  Sessions: 30 min - 24 hours
  Cache: 5 min - 1 hour
  OTP: 5 - 15 minutes
  Rate limit window: 1 - 60 seconds
  Temporary locks: 10 - 30 seconds
  Feature flags: 30 min - 24 hours
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Create session with 1-hour expiration
2. Generate and verify OTP (10 min expiration)
3. Implement email verification link (24 hour expiration)
4. Build password reset token (1 hour expiration)
5. Create temporary API key (30 day expiration)
6. Implement cache with different TTLs by type
7. Build rate limiter with sliding window
8. Create temporary feature flag system
9. Store temporary user preferences
10. Build automatic log cleanup

Challenge: Build complete authentication system:
  - Login creates session (1 hour)
  - OTP verification (10 min)
  - Password reset token (1 hour)
  - Remember-me token (30 days)
  - API keys (no expiration or custom)
  - Cleanup expired tokens daily

Modify the code and experiment!
""")
