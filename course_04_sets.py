"""
COURSE 4: SETS - Unique Items, Tags, and Intersections
=========================================================

THEORY:
Sets are unordered collections of UNIQUE values.
No duplicates allowed - Redis automatically deduplicates.

Key Concepts:
  - Unordered (no position)
  - Unique (duplicates ignored)
  - Fast membership testing O(1)
  - Set operations (intersection, union, difference)
  - Can grow very large

Common Operations:

1. SADD - Add Members
   SADD key member1 member2

2. SMEMBERS - Get All Members
   SMEMBERS key

3. SISMEMBER - Check Membership
   SISMEMBER key member

4. SREM - Remove Member
   SREM key member

5. SCARD - Set Size
   SCARD key

6. SINTER - Intersection
   SINTER key1 key2  (common members)

7. SUNION - Union
   SUNION key1 key2  (all members)

8. SDIFF - Difference
   SDIFF key1 key2   (in key1 but not key2)

9. SINTERSTORE - Store Intersection
   SINTERSTORE dest key1 key2

10. SPOP - Random Member
    SPOP key

11. SRANDMEMBER - Random Sample
    SRANDMEMBER key count

Performance:
  - SADD, SREM, SISMEMBER: O(1) - VERY FAST
  - SMEMBERS: O(N) - linear time
  - SINTER, SUNION, SDIFF: O(N*M) - slow for large sets

Use Cases:
  - Unique visitors to page
  - User tags & interests
  - Friend suggestions
  - Social following
  - Voting (unique voters)
  - Spam detection (unique IPs)
  - Data deduplication
"""

import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("SETS - PRACTICAL EXAMPLES WITH UJJAWAL SINGH")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. BASIC SADD & SMEMBERS
# ============================================================
print("1. BASIC SADD & SMEMBERS - Unique Tags")
print("-" * 70)

# Add tags to user
r.sadd(f"{user}:tags", "python", "redis", "docker", "python")  # python duplicate
print("Added tags: python, redis, docker, python (duplicate ignored)")

tags = r.smembers(f"{user}:tags")
print(f"Unique tags: {tags}")
print(f"Total unique tags: {r.scard(f'{user}:tags')}\n")

# ============================================================
# 2. SISMEMBER - Check Membership
# ============================================================
print("2. SISMEMBER - Does User Have Tag?")
print("-" * 70)

is_python = r.sismember(f"{user}:tags", "python")
is_java = r.sismember(f"{user}:tags", "java")

print(f"Has 'python' tag? {bool(is_python)}")
print(f"Has 'java' tag? {bool(is_java)}\n")

# ============================================================
# 3. SREM - Remove Members
# ============================================================
print("3. SREM - Remove Tags")
print("-" * 70)

print(f"Before: {r.smembers(f'{user}:tags')}")
r.srem(f"{user}:tags", "docker")
print(f"After removing 'docker': {r.smembers(f'{user}:tags')}\n")

# ============================================================
# 4. SET OPERATIONS - Intersection
# ============================================================
print("4. SET OPERATIONS - Find Common Interests")
print("-" * 70)

# User's interests
r.sadd(f"{user}:interests", "python", "javascript", "music", "gaming")

# Friend's interests
friend = "raj-singh"
r.sadd(f"{friend}:interests", "python", "java", "music", "movies")

print(f"Ujjawal interests: {r.smembers(f'{user}:interests')}")
print(f"Raj interests: {r.smembers(f'{friend}:interests')}")

# Find common interests (intersection)
common = r.sinter(f"{user}:interests", f"{friend}:interests")
print(f"Common interests: {common}\n")

# ============================================================
# 5. SUNION - Combine All Interests
# ============================================================
print("5. SUNION - All Interests Combined")
print("-" * 70)

all_interests = r.sunion(f"{user}:interests", f"{friend}:interests")
print(f"All interests (union): {all_interests}\n")

# ============================================================
# 6. SDIFF - Unique to One User
# ============================================================
print("6. SDIFF - Ujjawal's Unique Interests")
print("-" * 70)

ujjawal_unique = r.sdiff(f"{user}:interests", f"{friend}:interests")
print(f"Only Ujjawal has: {ujjawal_unique}\n")

# ============================================================
# 7. REAL-WORLD: Unique Page Visitors
# ============================================================
print("7. REAL-WORLD: Unique Visitors Counter")
print("-" * 70)

page_visitors = f"visitors:page:/profile/{user}"
r.delete(page_visitors)

# Simulate visitors (some IP repeats)
visitor_ips = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3",
    "192.168.1.1", "192.168.1.4",  # IP 1 visits again
    "192.168.1.2",                  # IP 2 visits again
    "192.168.1.5"
]

for ip in visitor_ips:
    r.sadd(page_visitors, ip)

unique_visitors = r.scard(page_visitors)
print(f"Total visits: {len(visitor_ips)}")
print(f"Unique visitors: {unique_visitors}")
print(f"Visitor IPs: {r.smembers(page_visitors)}\n")

# ============================================================
# 8. REAL-WORLD: Social Following (Friend Suggestions)
# ============================================================
print("8. REAL-WORLD: Friend Suggestions")
print("-" * 70)

# Ujjawal's followers
r.sadd(f"{user}:followers", "alice", "bob", "charlie", "diana")

# Raj's followers
r.sadd(f"{friend}:followers", "bob", "charlie", "eve", "frank")

# Find mutual followers (people who follow both)
mutual = r.sinter(f"{user}:followers", f"{friend}:followers")
print(f"Ujjawal followers: {r.smembers(f'{user}:followers')}")
print(f"Raj followers: {r.smembers(f'{friend}:followers')}")
print(f"Mutual followers: {mutual}")
print(f"(These people could be good group chat members!)\n")

# ============================================================
# 9. SINTERSTORE - Store Result
# ============================================================
print("9. SINTERSTORE - Store Intersection Result")
print("-" * 70)

mutual_key = f"{user}:mutual-followers-with-{friend}"
count = r.sinterstore(mutual_key, f"{user}:followers", f"{friend}:followers")
print(f"Stored {count} mutual followers")
print(f"Stored in: {mutual_key}")
print(f"Can retrieve later: {r.smembers(mutual_key)}\n")

# ============================================================
# 10. SPOP - Random Member
# ============================================================
print("10. SPOP - Random Selection")
print("-" * 70)

tags = f"{user}:random-tags"
r.sadd(tags, "python", "redis", "docker", "kubernetes", "golang")

print(f"All tags: {r.smembers(tags)}")

# Pick random tags for daily highlight
random_tag = r.spop(tags)
print(f"Random tag selected (removed): {random_tag}")
print(f"Remaining tags: {r.smembers(tags)}\n")

# Reset
r.sadd(tags, random_tag)

# ============================================================
# 11. SRANDMEMBER - Random Sample (keep members)
# ============================================================
print("11. SRANDMEMBER - Random Sample (doesn't remove)")
print("-" * 70)

print(f"All tags: {r.smembers(tags)}")

# Pick 3 random tags for recommendations
sample = r.srandmember(tags, 3)
print(f"Random 3 tags (kept): {sample}")
print(f"All tags still there: {r.smembers(tags)}\n")

# ============================================================
# 12. REAL-WORLD: Spam Detection
# ============================================================
print("12. REAL-WORLD: Spam Detection")
print("-" * 70)

# Legitimate IPs
r.sadd(f"{user}:legitimate-ips", "203.0.113.1", "203.0.113.2", "203.0.113.3")

# Blocked IPs
r.sadd(f"{user}:blocked-ips", "192.0.2.1", "192.0.2.2", "203.0.113.2")

incoming_ip = "203.0.113.2"
is_blocked = r.sismember(f"{user}:blocked-ips", incoming_ip)
print(f"Check if {incoming_ip} is blocked: {bool(is_blocked)}")
print(f"Decision: {'BLOCK' if is_blocked else 'ALLOW'}\n")

# ============================================================
# 13. REAL-WORLD: Voting System
# ============================================================
print("13. REAL-WORLD: Voting (Unique Voters)")
print("-" * 70)

poll_id = "poll:best-language"
r.delete(poll_id)

# Simulate votes (some users vote twice, but only count once)
voters = ["ujjawal", "raj", "priya", "ujjawal", "john", "priya", "raj"]

for voter in voters:
    r.sadd(poll_id, voter)

unique_votes = r.scard(poll_id)
print(f"Total vote attempts: {len(voters)}")
print(f"Unique voters: {unique_votes}")
print(f"Voter IDs: {r.smembers(poll_id)}\n")

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("SETS - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Add/Remove:
  SADD key member              - Add member
  SREM key member              - Remove member
  SPOP key                     - Remove & return random

Query:
  SMEMBERS key                 - Get all members
  SISMEMBER key member         - Check membership
  SCARD key                    - Get size
  SRANDMEMBER key count        - Get random members

Set Operations:
  SINTER key1 key2            - Intersection (common)
  SUNION key1 key2            - Union (all)
  SDIFF key1 key2             - Difference (in key1 not key2)
  SINTERSTORE dest k1 k2      - Store intersection

Use Cases:
  [OK] Unique collections
  [OK] Tags and categories
  [OK] Followers and following
  [OK] Unique visitors
  [OK] Voting (unique voters)
  [OK] Friend suggestions
  [OK] Spam detection
  [OK] Data deduplication

Performance:
  [FAST] SADD, SREM, SISMEMBER = O(1)
  [SLOW] SMEMBERS, SINTER, SUNION = O(N)
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Create user skills and find common skills between 2 users
2. Build a "people you may know" feature using set intersection
3. Create voting system with unique voters only
4. Track unique page visitors per day
5. Build a tag system with tag suggestions
6. Create spam filter with blocked IP addresses
7. Build mutual followers feature for social app
8. Track unique downloads by IP address
9. Create recommendation system based on common interests
10. Build deduplication system for emails

Challenge: Build a complete recommendation engine:
  - Store skills for 5 users
  - Find users with common skills
  - Suggest friends based on shared interests
  - Track unique suggestions (no duplicates)

Modify the code and experiment!
""")
