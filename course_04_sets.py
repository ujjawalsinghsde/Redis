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
friend = "alice-doe"
r.sadd(f"{friend}:interests", "python", "java", "music", "movies")

print(f"Ujjawal interests: {r.smembers(f'{user}:interests')}")
print(f"Alice interests: {r.smembers(f'{friend}:interests')}")

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
r.sadd(f"{user}:followers", "john", "bob", "charlie", "diana")

# Alice's followers
r.sadd(f"{friend}:followers", "bob", "charlie", "eve", "frank")

# Find mutual followers (people who follow both)
mutual = r.sinter(f"{user}:followers", f"{friend}:followers")
print(f"Ujjawal followers: {r.smembers(f'{user}:followers')}")
print(f"Alice followers: {r.smembers(f'{friend}:followers')}")
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
voters = ["ujjawal", "alice", "priya", "ujjawal", "john", "priya", "alice"]

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

# ============================================================
# PRACTICE: Solutions for Sets
# ============================================================
print("="*70)
print("PRACTICE: Sets Exercises")
print("="*70 + "\n")

# 1. Create user skills and find common skills between 2 users
print("1. User skills & common skills")
print("-" * 70)
alice_skills = "skills:alice"
bob_skills = "skills:bob"
r.delete(alice_skills, bob_skills)
r.sadd(alice_skills, "python", "redis", "docker", "javascript")
r.sadd(bob_skills, "python", "java", "docker", "aws")
print("  Alice skills:", r.smembers(alice_skills))
print("  Bob skills:", r.smembers(bob_skills))
print("  Common skills:", r.sinter(alice_skills, bob_skills))
print()

# 2. Build a "people you may know" feature using set intersection
print("2. People you may know")
print("-" * 70)
alice_friends = "friends:alice"
bob_friends = "friends:bob"
carol_friends = "friends:carol"
r.delete(alice_friends, bob_friends, carol_friends)
r.sadd(alice_friends, "bob", "carol", "dave")
r.sadd(bob_friends, "alice", "emma", "frank")
r.sadd(carol_friends, "alice", "gina", "harry")

maybe_you_know = r.sunion(bob_friends, carol_friends)
direct_friends = r.smembers(alice_friends)
suggestions = sorted(set(maybe_you_know) - direct_friends - {"alice"})
print("  Candidate suggestions for Alice:", suggestions)
print()

# 3. Create voting system with unique voters only
print("3. Voting system with unique voters")
print("-" * 70)
poll_id = "poll:best-editor"
r.delete(poll_id)
votes = ["alice", "bob", "alice", "carol", "dave", "bob"]
for voter in votes:
  r.sadd(poll_id, voter)
print("  Vote attempts:", votes)
print("  Unique voters:", r.scard(poll_id))
print("  Voter IDs:", r.smembers(poll_id))
print()

# 4. Track unique page visitors per day
print("4. Unique page visitors per day")
print("-" * 70)
from datetime import date

today = date.today().isoformat()
visitors_key = f"visitors:/profile/{user}:{today}"
r.delete(visitors_key)
visitor_ips = ["10.0.0.1", "10.0.0.2", "10.0.0.1", "10.0.0.3"]
for ip in visitor_ips:
  r.sadd(visitors_key, ip)
print("  Total attempts:", len(visitor_ips))
print("  Unique visitors today:", r.scard(visitors_key))
print()

# 5. Build a tag system with tag suggestions
print("5. Tag suggestions")
print("-" * 70)
post1 = "post:1:tags"
post2 = "post:2:tags"
post3 = "post:3:tags"
r.delete(post1, post2, post3)
r.sadd(post1, "python", "redis", "backend")
r.sadd(post2, "javascript", "frontend", "react")
r.sadd(post3, "python", "ml", "data")

python_posts = r.sunion(post1, post3)
print("  Suggested tags for python posts:", python_posts)
print()

# 6. Create spam filter with blocked IP addresses
print("6. Spam filter")
print("-" * 70)
blocked_ips = f"{user}:blocked-ips"
r.delete(blocked_ips)
r.sadd(blocked_ips, "192.0.2.1", "203.0.113.5")
incoming_ip = "203.0.113.5"
print(f"  Is {incoming_ip} blocked?", bool(r.sismember(blocked_ips, incoming_ip)))
print()

# 7. Build mutual followers feature for social app
print("7. Mutual followers")
print("-" * 70)
user_followers = f"{user}:followers"
alice_followers = "alice-doe:followers"
r.delete(user_followers, alice_followers)
r.sadd(user_followers, "john", "bob", "charlie")
r.sadd(alice_followers, "bob", "elena", "charlie")
print("  Mutual followers:", r.sinter(user_followers, alice_followers))
print()

# 8. Track unique downloads by IP address
print("8. Unique downloads by IP")
print("-" * 70)
download_key = "downloads:file123"
r.delete(download_key)
download_ips = ["8.8.8.8", "8.8.4.4", "8.8.8.8"]
for ip in download_ips:
  r.sadd(download_key, ip)
print("  Unique downloaders:", r.scard(download_key))
print("  IPs:", r.smembers(download_key))
print()

# 9. Create recommendation system based on common interests
print("9. Recommendation system")
print("-" * 70)
interest_keys = {
  "u1": "interests:u1",
  "u2": "interests:u2",
  "u3": "interests:u3",
}
r.delete(*interest_keys.values())
r.sadd(interest_keys["u1"], "python", "redis", "ml")
r.sadd(interest_keys["u2"], "python", "aws", "docker")
r.sadd(interest_keys["u3"], "java", "redis", "docker")

def common_interest_recommendations(target_key, candidate_keys):
  results = []
  for name, key in candidate_keys.items():
    if key == target_key:
      continue
    common = r.sinter(target_key, key)
    results.append((key, len(common), common))
  results.sort(key=lambda item: item[1], reverse=True)
  return results

print("  Recommendations for u1:", common_interest_recommendations(interest_keys["u1"], interest_keys))
print()

# 10. Build deduplication system for emails
print("10. Email deduplication")
print("-" * 70)
emails_key = "emails:subscribers"
r.delete(emails_key)
emails = ["A@EXAMPLE.com", "a@example.com", "bob@example.com"]
for email in emails:
  r.sadd(emails_key, email.strip().lower())
print("  Unique normalized emails:", r.smembers(emails_key))
print()

# Challenge: complete recommendation engine
print("CHALLENGE: Recommendation engine")
print("-" * 70)
skill_keys = {
  "alice": "skills:engine:alice",
  "bob": "skills:engine:bob",
  "carol": "skills:engine:carol",
  "dave": "skills:engine:dave",
  "erin": "skills:engine:erin",
}
r.delete(*skill_keys.values())
r.sadd(skill_keys["alice"], "python", "redis", "docker")
r.sadd(skill_keys["bob"], "python", "aws")
r.sadd(skill_keys["carol"], "java", "spring")
r.sadd(skill_keys["dave"], "python", "ml")
r.sadd(skill_keys["erin"], "redis", "docker")

def suggest_friends(target_name, key_map, min_common=1):
  target_key = key_map[target_name]
  target_skills = r.smembers(target_key)
  suggestion_key = f"suggestions:{target_name}"
  r.delete(suggestion_key)
  for other_name, other_key in key_map.items():
    if other_name == target_name:
      continue
    common = r.sinter(target_key, other_key)
    if len(common) >= min_common:
      r.sadd(suggestion_key, other_name)
  return target_skills, r.smembers(suggestion_key)

skills, suggested = suggest_friends("alice", skill_keys)
print("  Alice skills:", skills)
print("  Suggested friends (unique):", suggested)
print()

print("ALL SETS PRACTICE PROBLEMS COMPLETED")
print("="*70)
