"""
COURSE 12: SESSION MANAGEMENT - User Login & State
====================================================

Sessions store user state between requests.
Redis is perfect for fast, scalable sessions.

Session Lifecycle:
  1. User logs in → Create session
  2. Store session data → Hash/String
  3. Set expiration → TTL (1-24 hours)
  4. Check session on request → Get from Redis
  5. Session expires → Auto-delete

Session Storage in Redis:
  session:{session_id}:user_id, login_time, ip, etc.
  or use Hash: HSET session:{id} user_id ...

Benefits:
  - Fast (memory)
  - Scalable (distributed)
  - Can share across servers
  - Auto-cleanup with TTL
"""

import redis
import time
import uuid

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("SESSION MANAGEMENT - USER LOGIN")
print("="*70 + "\n")

# ============================================================
# 1. CREATE SESSION
# ============================================================
print("1. CREATE SESSION - User Logs In")
print("-" * 70)

def create_session(user_id, user_data):
    """Create session for logged-in user"""
    session_id = str(uuid.uuid4())  # Unique session ID
    session_key = f"session:{session_id}"

    # Store session data
    r.hset(session_key, mapping={
        "user_id": user_id,
        "username": user_data["username"],
        "role": user_data.get("role", "user"),
        "created_at": str(time.time()),
        "ip_address": "203.0.113.5"
    })

    # Set expiration (1 hour)
    r.expire(session_key, 3600)

    return session_id

user_data = {"username": "ujjawal-singh", "role": "admin"}
session_id = create_session("ujjawal", user_data)
print(f"Session created: {session_id}")
print(f"Expires in: 3600 seconds (1 hour)\n")

# ============================================================
# 2. GET SESSION
# ============================================================
print("2. GET SESSION - Retrieve User Data")
print("-" * 70)

def get_session(session_id):
    """Get session data"""
    return r.hgetall(f"session:{session_id}")

session = get_session(session_id)
print(f"Session data:")
for key, value in session.items():
    print(f"  {key}: {value}")
print()

# ============================================================
# 3. UPDATE SESSION
# ============================================================
print("3. UPDATE SESSION - Extend Expiration")
print("-" * 70)

session_key = f"session:{session_id}"
r.expire(session_key, 3600)  # Reset to 1 hour
print(f"Session refreshed - TTL reset to 3600s\n")

# ============================================================
# 4. CHECK SESSION VALIDITY
# ============================================================
print("4. CHECK SESSION VALIDITY")
print("-" * 70)

def is_session_valid(session_id):
    """Check if session exists"""
    ttl = r.ttl(f"session:{session_id}")
    return ttl > 0

valid = is_session_valid(session_id)
print(f"Session {session_id[:8]}... valid? {valid}\n")

# ============================================================
# 5. LOGOUT - DESTROY SESSION
# ============================================================
print("5. LOGOUT - Destroy Session")
print("-" * 70)

def logout_user(session_id):
    """Logout user"""
    r.delete(f"session:{session_id}")

print("User logs out...")
logout_user(session_id)

valid = is_session_valid(session_id)
print(f"Session valid after logout? {valid}\n")

# ============================================================
# 6. REAL-WORLD: Multi-Device Sessions
# ============================================================
print("6. REAL-WORLD: Multiple Devices")
print("-" * 70)

def login_user(user_id):
    """User logs in from new device"""
    session_id = str(uuid.uuid4())
    r.hset(f"session:{session_id}", mapping={
        "user_id": user_id,
        "device": "mobile"
    })
    r.expire(f"session:{session_id}", 3600)

    # Track all sessions for user
    r.sadd(f"user:{user_id}:sessions", session_id)
    return session_id

user_id = "ujjawal"

# Login from mobile
session1 = login_user(user_id)
print(f"Logged in from mobile: {session1[:8]}...")

# Login from desktop
session2 = login_user(user_id)
print(f"Logged in from desktop: {session2[:8]}...")

sessions = r.smembers(f"user:{user_id}:sessions")
print(f"Active sessions: {len(sessions)}\n")

# ============================================================
# 7. REAL-WORLD: Remember-Me
# ============================================================
print("7. REAL-WORLD: Remember-Me (Persistent Login)")
print("-" * 70)

def create_remember_token(user_id):
    """Create long-lived remember token"""
    token = str(uuid.uuid4())
    r.hset(f"remember:{token}", mapping={
        "user_id": user_id,
        "created_at": str(time.time())
    })
    # 30-day expiration
    r.expire(f"remember:{token}", 30 * 24 * 3600)
    return token

remember_token = create_remember_token(user_id)
print(f"Remember-me token: {remember_token[:8]}...")
print(f"Expires in: 30 days\n")

# ============================================================
# SUMMARY - SESSION MANAGEMENT
# ============================================================
print("="*70)
print("SESSION MANAGEMENT - KEY OPERATIONS")
print("="*70)
print("""
Create Session:
  session_id = UUID
  HSET session:{id} user_id ... (with data)
  EXPIRE session:{id} 3600      (1 hour)

Use Session:
  HGETALL session:{id}          (Get data)
  EXPIRE session:{id} 3600      (Extend TTL)

Logout:
  DEL session:{id}              (Delete)

Track User Sessions:
  SADD user:{id}:sessions sid   (Track)
  SMEMBERS user:{id}:sessions   (List all)

Session Best Practices:
  [OK] Use UUID for session ID
  [OK] Hash for session data
  [OK] TTL for auto-cleanup
  [OK] Refresh on activity
  [OK] Track multiple sessions
  [OK] Logout clears session
  [OK] Remember-me separate

Session Timeouts:
  - Web app: 15 min - 1 hour
  - Mobile app: 7 days
  - Remember-me: 30 days
  - API key: custom or none

Security:
  - Store user_id in session
  - Validate on each request
  - Regenerate ID after login
  - Use HTTPS with secure cookies
  - Log suspicious activity
""")

print("\n" + "="*70)
print("COURSE 13: RATE LIMITING - Protect APIs")
print("="*70 + "\n")

print("""
Rate Limiting prevents abuse by limiting requests.

Strategies:
1. Token Bucket: Fixed capacity, fills over time
2. Sliding Window: Count requests in time window
3. Fixed Window: Count requests per fixed period
""")

r.flushdb()

# ============================================================
# RATE LIMITING - Token Bucket
# ============================================================
print("1. TOKEN BUCKET ALGORITHM")
print("-" * 70)

def rate_limit_token_bucket(user_id, limit=10, window=60):
    """Token bucket rate limiter"""
    key = f"rate:{user_id}"

    count = r.incr(key)
    if count == 1:
        r.expire(key, window)

    return count <= limit

print("Simulating API requests (limit 10/min):")
for i in range(12):
    allowed = rate_limit_token_bucket("user123", limit=10, window=60)
    status = "ALLOWED" if allowed else "BLOCKED"
    print(f"  Request {i+1}: {status}")
print()

# ============================================================
# RATE LIMITING - Per Endpoint
# ============================================================
print("2. RATE LIMIT PER ENDPOINT")
print("-" * 70)

def api_call(user_id, endpoint, limit=100):
    """Rate limit specific endpoint"""
    key = f"api:{endpoint}:{user_id}"
    count = r.incr(key)

    if count == 1:
        r.expire(key, 60)

    return count <= limit

# Different limits for different endpoints
endpoints = {
    "search": 100,
    "create": 50,
    "upload": 10
}

for endpoint, limit in endpoints.items():
    allowed = api_call("user123", endpoint, limit)
    print(f"  {endpoint}: {'OK' if allowed else 'BLOCKED'}")
print()

# ============================================================
# RATE LIMITING - REAL-WORLD
# ============================================================
print("3. REAL-WORLD: API RATE LIMITING")
print("-" * 70)

print("API plan limits:")
print("  Free: 100 requests/hour")
print("  Pro: 1000 requests/hour")
print("  Enterprise: unlimited")
print()

# ============================================================
# SUMMARY - RATE LIMITING
# ============================================================
print("="*70)
print("RATE LIMITING - COMMANDS")
print("="*70)
print("""
Simple Counter:
  INCR rate:{user}
  EXPIRE rate:{user} 60

Check Limit:
  count = GET rate:{user}
  if count > limit: BLOCK

Per-Endpoint:
  INCR rate:{endpoint}:{user}
  Different limits per endpoint

Strategies:
  - Token Bucket: Fill over time
  - Sliding Window: Window moves
  - Fixed Window: Per minute/hour
  - User tiers: Different limits

Common Limits:
  - API: 100-1000 per hour
  - Login: 5-10 per minute
  - Search: 100 per minute
  - Upload: 10 per hour
""")

print("\n" + "="*70)
print("COURSE 14: TASK QUEUES - Job Processing")
print("="*70 + "\n")

print("""
Task queues process jobs asynchronously.
Producer adds tasks, workers process.
""")

r.flushdb()

# ============================================================
# TASK QUEUE - Producer
# ============================================================
print("1. TASK QUEUE - Producer")
print("-" * 70)

def enqueue_task(task_type, data):
    """Add task to queue"""
    import json
    task = {"type": task_type, "data": data}
    r.rpush("tasks:queue", json.dumps(task))
    print(f"  Queued: {task_type}")

print("Enqueueing tasks:")
enqueue_task("send_email", {"to": "user@example.com"})
enqueue_task("generate_report", {"report_id": 123})
enqueue_task("process_image", {"image_id": 456})
print()

# ============================================================
# TASK QUEUE - Consumer
# ============================================================
print("2. TASK QUEUE - Consumer/Worker")
print("-" * 70)

def process_queue():
    """Process tasks from queue"""
    import json

    while True:
        task_json = r.lpop("tasks:queue")
        if not task_json:
            break

        task = json.loads(task_json)
        print(f"  Processing: {task['type']}")

print("Processing queue:")
process_queue()
print()

# ============================================================
# SUMMARY - TASK QUEUES
# ============================================================
print("="*70)
print("TASK QUEUES - COMMANDS")
print("="*70)
print("""
Enqueue:
  RPUSH tasks:{queue} {json}

Dequeue:
  LPOP tasks:{queue}

FIFO Processing:
  - RPUSH: Add to end
  - LPOP: Take from beginning

Priority Queues:
  - Multiple queues (high, normal, low)
  - Process high priority first

Dead Letter Queue:
  - Failed tasks moved to {queue}:failed
  - Review and retry later

Common Patterns:
  - Email sending
  - Report generation
  - Image processing
  - Data import
  - Backup jobs
  - Notifications
""")

print("\n" + "="*70)
print("ALL 14 COURSES COMPLETED!")
print("="*70)
print("""
You now have comprehensive knowledge of:
  [OK] Core data types (strings, lists, sets, hashes, sorted sets)
  [OK] Advanced features (expiration, transactions, pub/sub)
  [OK] Persistence (RDB, AOF, backup)
  [OK] Production patterns (caching, sessions, rate limiting, queues)

Next: Build real projects combining all these!
""")
