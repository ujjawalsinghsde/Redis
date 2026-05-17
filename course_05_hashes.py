"""
COURSE 5: HASHES - Objects, Profiles, and Key-Value Pairs
===========================================================

THEORY:
Hashes are maps of field-value pairs (like objects/dictionaries).
Perfect for storing structured data.

Key Concepts:
  - Field-value pairs (like dict or JSON)
  - Can store multiple fields per key
  - Each field can be accessed independently
  - Efficient for partial updates
  - Great for storing objects

Common Operations:

1. HSET - Set Fields
   HSET key field value [field value ...]

2. HGET - Get Single Field
   HGET key field

3. HGETALL - Get All Fields
   HGETALL key

4. HMGET - Get Multiple Fields
   HMGET key field1 field2

5. HDEL - Delete Fields
   HDEL key field

6. HEXISTS - Check Field Exists
   HEXISTS key field

7. HLEN - Number of Fields
   HLEN key

8. HKEYS - Get All Fields (names)
   HKEYS key

9. HVALS - Get All Values
   HVALS key

10. HINCRBY - Increment Field
    HINCRBY key field increment

11. HINCRBYFLOAT - Increment Float
    HINCRBYFLOAT key field increment

12. HSETNX - Set Only if Not Exists
    HSETNX key field value

Performance:
  - HSET, HGET, HDEL, HEXISTS: O(1)
  - HGETALL, HKEYS, HVALS: O(N) where N = fields
  - Good for storing objects

Use Cases:
  - User profiles
  - Product information
  - Configuration objects
  - Session data
  - Settings & preferences
  - Counters per category
"""

import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("HASHES - PRACTICAL EXAMPLES WITH UJJAWAL SINGH")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. BASIC HSET & HGET
# ============================================================
print("1. BASIC HSET & HGET - Store User Profile")
print("-" * 70)

# Set multiple fields at once
r.hset(f"{user}:profile", mapping={
    "name": "Ujjawal Singh",
    "email": "ujjawal@example.com",
    "age": "25",
    "location": "India",
    "job_title": "Software Engineer"
})

print(f"Name: {r.hget(f'{user}:profile', 'name')}")
print(f"Email: {r.hget(f'{user}:profile', 'email')}")
print(f"Location: {r.hget(f'{user}:profile', 'location')}\n")

# ============================================================
# 2. HGETALL - Get All Fields
# ============================================================
print("2. HGETALL - Get Complete Profile")
print("-" * 70)

profile = r.hgetall(f"{user}:profile")
print(f"Full profile:")
for field, value in profile.items():
    print(f"  {field}: {value}")
print()

# ============================================================
# 3. HMGET - Get Specific Fields
# ============================================================
print("3. HMGET - Get Multiple Specific Fields")
print("-" * 70)

fields_needed = ["name", "email", "job_title"]
values = r.hmget(f"{user}:profile", fields_needed)

for field, value in zip(fields_needed, values):
    print(f"{field}: {value}")
print()

# ============================================================
# 4. HINCRBY - Increment Field
# ============================================================
print("4. HINCRBY - Track Statistics")
print("-" * 70)

# Initialize stats
r.hset(f"{user}:stats", mapping={
    "posts": 0,
    "followers": 100,
    "likes": 500
})

print(f"Before:")
print(f"  Posts: {r.hget(f'{user}:stats', 'posts')}")
print(f"  Followers: {r.hget(f'{user}:stats', 'followers')}")

# Create new post
r.hincrby(f"{user}:stats", "posts", 1)
print(f"\nAfter new post:")
print(f"  Posts: {r.hget(f'{user}:stats', 'posts')}")

# Get likes on post
r.hincrby(f"{user}:stats", "likes", 25)
print(f"After 25 likes:")
print(f"  Likes: {r.hget(f'{user}:stats', 'likes')}\n")

# ============================================================
# 5. HEXISTS & HDEL
# ============================================================
print("5. HEXISTS - Check Field & HDEL - Remove Field")
print("-" * 70)

exists = r.hexists(f"{user}:profile", "phone")
print(f"Has phone field? {bool(exists)}")

r.hset(f"{user}:profile", "phone", "9876543210")
exists = r.hexists(f"{user}:profile", "phone")
print(f"After setting phone: {bool(exists)}")

r.hdel(f"{user}:profile", "phone")
exists = r.hexists(f"{user}:profile", "phone")
print(f"After deleting phone: {bool(exists)}\n")

# ============================================================
# 6. HKEYS & HVALS
# ============================================================
print("6. HKEYS & HVALS - Get Field Names & Values")
print("-" * 70)

keys = r.hkeys(f"{user}:profile")
values = r.hvals(f"{user}:profile")

print(f"Fields: {keys}")
print(f"Values: {values}\n")

# ============================================================
# 7. HLEN - Count Fields
# ============================================================
print("7. HLEN - Count Profile Fields")
print("-" * 70)

field_count = r.hlen(f"{user}:profile")
print(f"Total profile fields: {field_count}\n")

# ============================================================
# 8. REAL-WORLD: Product Information
# ============================================================
print("8. REAL-WORLD: E-Commerce Product Storage")
print("-" * 70)

product_id = "product:laptop-001"
r.hset(product_id, mapping={
    "name": "MacBook Pro",
    "price": "1299.99",
    "brand": "Apple",
    "stock": "45",
    "rating": "4.8",
    "reviews": "1205",
    "sku": "MBP-2023-13"
})

product = r.hgetall(product_id)
print(f"Product: {product['name']}")
print(f"Price: ${product['price']}")
print(f"Stock: {product['stock']} units")
print(f"Rating: {product['rating']}/5 ({product['reviews']} reviews)\n")

# ============================================================
# 9. REAL-WORLD: Session Storage
# ============================================================
print("9. REAL-WORLD: User Session Management")
print("-" * 70)

session_id = "session:ujjawal-xyz789"
r.hset(session_id, mapping={
    "user_id": user,
    "username": "ujjawal_singh",
    "logged_in_at": str(datetime.now()),
    "ip_address": "203.0.113.5",
    "user_agent": "Mozilla/5.0...",
    "role": "admin"
})

# Set expiration (session expires in 1 hour)
r.expire(session_id, 3600)

session = r.hgetall(session_id)
print(f"Session user: {session['username']}")
print(f"Logged in at: {session['logged_in_at']}")
print(f"Role: {session['role']}\n")

# ============================================================
# 10. REAL-WORLD: Settings & Configuration
# ============================================================
print("10. REAL-WORLD: User Settings")
print("-" * 70)

settings_key = f"{user}:settings"
r.hset(settings_key, mapping={
    "theme": "dark",
    "notifications": "enabled",
    "language": "english",
    "privacy": "friends_only",
    "two_factor": "enabled",
    "email_digest": "weekly"
})

settings = r.hgetall(settings_key)
print(f"User settings:")
for key, value in settings.items():
    print(f"  {key}: {value}")
print()

# ============================================================
# 11. REAL-WORLD: Counters Per Category
# ============================================================
print("11. REAL-WORLD: Content Counters")
print("-" * 70)

content_stats = "stats:content:2024"
r.hset(content_stats, mapping={
    "blog_posts": 0,
    "videos": 0,
    "podcasts": 0,
    "tutorials": 0
})

print("Publishing new content...")

# Publish different types
r.hincrby(content_stats, "blog_posts", 1)
r.hincrby(content_stats, "blog_posts", 1)
r.hincrby(content_stats, "videos", 3)
r.hincrby(content_stats, "tutorials", 5)

print(f"Content published:")
for content_type, count in r.hgetall(content_stats).items():
    print(f"  {content_type}: {count}")
print()

# ============================================================
# 12. REAL-WORLD: Form Data Storage
# ============================================================
print("12. REAL-WORLD: Form Submission Storage")
print("-" * 70)

form_id = "form:contact-ujjawal-2024-05-18"
r.hset(form_id, mapping={
    "name": "Ujjawal Singh",
    "email": "ujjawal@example.com",
    "subject": "Question about Redis",
    "message": "How to scale Redis?",
    "submitted_at": str(datetime.now()),
    "status": "pending"
})

form_data = r.hgetall(form_id)
print(f"Form submission:")
for field, value in form_data.items():
    print(f"  {field}: {value}")
print()

# ============================================================
# 13. HSETNX - Set Only if Not Exists
# ============================================================
print("13. HSETNX - Set Only if Not Exists")
print("-" * 70)

profile = f"{user}:profile-v2"

# Set phone only if not already set
result1 = r.hsetnx(profile, "phone", "9876543210")
print(f"First time setting phone: {bool(result1)} (1=success)")

# Try again
result2 = r.hsetnx(profile, "phone", "1234567890")
print(f"Second time setting phone: {bool(result2)} (0=failed, already exists)")
print(f"Phone value: {r.hget(profile, 'phone')}\n")

# ============================================================
# 14. HINCRBYFLOAT - Float Operations
# ============================================================
print("14. HINCRBYFLOAT - Float Increments")
print("-" * 70)

account = f"{user}:account"
r.hset(account, "balance", "1000.50")

print(f"Initial balance: ${r.hget(account, 'balance')}")

r.hincrbyfloat(account, "balance", 50.25)
print(f"After deposit of $50.25: ${r.hget(account, 'balance')}")

r.hincrbyfloat(account, "balance", -25.75)
print(f"After withdrawal of $25.75: ${r.hget(account, 'balance')}\n")

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("HASHES - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Set:
  HSET key field value         - Set single field
  HSET key mapping={...}       - Set multiple fields
  HSETNX key field value       - Set if not exists

Get:
  HGET key field               - Get single field
  HGETALL key                  - Get all fields & values
  HMGET key field1 field2      - Get multiple fields
  HKEYS key                    - Get all field names
  HVALS key                    - Get all values

Modify:
  HDEL key field               - Delete field
  HINCRBY key field 1          - Increment integer
  HINCRBYFLOAT key field 1.5   - Increment float

Query:
  HEXISTS key field            - Check if field exists
  HLEN key                     - Count fields

Use Cases:
  [OK] User profiles
  [OK] Product information
  [OK] Session storage
  [OK] Configuration/settings
  [OK] Form submissions
  [OK] Counters per category
  [OK] Key-value configurations
  [OK] Financial accounts

Performance:
  [FAST] HSET, HGET, HDEL = O(1)
  [MEDIUM] HGETALL, HKEYS, HVALS = O(N)
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Store complete user profile (20+ fields) in hash
2. Create product catalog with multiple products
3. Build shopping cart using hashes
4. Store settings for 5 different apps
5. Create account ledger with balance tracking
6. Build form submission storage system
7. Store student grades across subjects
8. Create API response caching with hashes
9. Track inventory with stock counters
10. Build user preferences system

Challenge: Build complete user account system:
  - Profile information (name, email, age, location)
  - Settings (theme, language, notifications)
  - Statistics (posts, followers, likes)
  - Account (balance, credits, subscription)
  - All in separate hashes linked by user ID
  - Can retrieve any field instantly

Modify the code and experiment!
""")
