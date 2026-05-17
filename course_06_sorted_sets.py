"""
COURSE 6: SORTED SETS - Leaderboards and Rankings
===================================================

THEORY:
Sorted Sets are like Sets but with a SCORE for each member.
Members are ordered by score. Perfect for leaderboards.

Key Concepts:
  - Members have associated SCORES
  - Members ordered by score (low to high)
  - Unique members (no duplicates)
  - Fast range queries
  - Can have duplicate scores

Common Operations:

1. ZADD - Add Members with Scores
   ZADD key score member [score member ...]

2. ZRANGE - Get by Rank (low to high)
   ZRANGE key start stop [WITHSCORES]

3. ZREVRANGE - Get by Rank (high to low)
   ZREVRANGE key start stop [WITHSCORES]

4. ZSCORE - Get Member Score
   ZSCORE key member

5. ZRANK - Get Member Rank (position)
   ZRANK key member

6. ZREVRANK - Get Member Rank (reverse)
   ZREVRANK key member

7. ZCARD - Count Members
   ZCARD key

8. ZREM - Remove Member
   ZREM key member

9. ZINCRBY - Increment Score
   ZINCRBY key increment member

10. ZCOUNT - Count Members in Score Range
    ZCOUNT key min max

Performance:
  - ZADD, ZREM, ZSCORE: O(log N)
  - ZRANGE, ZREVRANGE: O(log N + M) where M = returned
  - ZRANK: O(log N)
  - Great for leaderboards!

Use Cases:
  - Leaderboards
  - Top N queries
  - Sorted feeds
  - Priority queues
  - Ratings & rankings
  - Time-based sorting
  - Scoring systems
"""

import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("SORTED SETS - LEADERBOARDS WITH UJJAWAL SINGH")
print("="*70 + "\n")

# ============================================================
# 1. BASIC ZADD
# ============================================================
print("1. BASIC ZADD - Build Leaderboard")
print("-" * 70)

leaderboard = "leaderboard:global"

# Add players with scores
r.zadd(leaderboard, {
    "ujjawal-singh": 1000,
    "raj-singh": 950,
    "priya-sharma": 1200,
    "john-doe": 800,
    "diana-prince": 1100
})

print("Players added to leaderboard\n")

# ============================================================
# 2. ZRANGE & ZREVRANGE - Get Rankings
# ============================================================
print("2. ZREVRANGE - Top 5 Players (High to Low)")
print("-" * 70)

top5 = r.zrevrange(leaderboard, 0, 4, withscores=True)
print("Rank | Player          | Score")
print("-" * 40)
for rank, (player, score) in enumerate(top5, 1):
    print(f"{rank:4} | {player:15} | {int(score)}")
print()

# ============================================================
# 3. ZSCORE - Get Individual Score
# ============================================================
print("3. ZSCORE - Check Ujjawal's Score")
print("-" * 70)

score = r.zscore(leaderboard, "ujjawal-singh")
print(f"Ujjawal's score: {int(score)}\n")

# ============================================================
# 4. ZRANK & ZREVRANK - Get Position
# ============================================================
print("4. ZRANK - Get Ujjawal's Rank")
print("-" * 70)

rank = r.zrevrank(leaderboard, "ujjawal-singh")
print(f"Ujjawal is ranked: #{rank + 1} (0-indexed)")
print()

# ============================================================
# 5. ZINCRBY - Update Score
# ============================================================
print("5. ZINCRBY - Players Earn Points")
print("-" * 70)

print(f"Ujjawal before: {int(r.zscore(leaderboard, 'ujjawal-singh'))} points")

# Ujjawal wins a game and gets 100 points
r.zincrby(leaderboard, 100, "ujjawal-singh")

print(f"Ujjawal after: {int(r.zscore(leaderboard, 'ujjawal-singh'))} points")
print(f"New rank: #{r.zrevrank(leaderboard, 'ujjawal-singh') + 1}\n")

# ============================================================
# 6. ZCARD - Total Players
# ============================================================
print("6. ZCARD - Count Total Players")
print("-" * 70)

total_players = r.zcard(leaderboard)
print(f"Total players: {total_players}\n")

# ============================================================
# 7. ZCOUNT - Count in Score Range
# ============================================================
print("7. ZCOUNT - Players in Score Range")
print("-" * 70)

high_scorers = r.zcount(leaderboard, 1000, 1300)
print(f"Players with 1000-1300 points: {high_scorers}\n")

# ============================================================
# 8. REAL-WORLD: Game Leaderboard (Progressive)
# ============================================================
print("8. REAL-WORLD: Game Leaderboard Updates")
print("-" * 70)

game_leaderboard = "leaderboard:game-2024"

# Day 1
print("Day 1 Results:")
r.zadd(game_leaderboard, {
    "player1": 500,
    "player2": 450,
    "player3": 400
})

for rank, (player, score) in enumerate(r.zrevrange(game_leaderboard, 0, -1, withscores=True), 1):
    print(f"  {rank}. {player}: {int(score)}")

# Day 2 - Players earn more points
print("\nDay 2 - After playing more games:")
r.zincrby(game_leaderboard, 200, "player1")
r.zincrby(game_leaderboard, 250, "player2")
r.zincrby(game_leaderboard, 100, "player3")

for rank, (player, score) in enumerate(r.zrevrange(game_leaderboard, 0, -1, withscores=True), 1):
    print(f"  {rank}. {player}: {int(score)}")
print()

# ============================================================
# 9. REAL-WORLD: Multiple Leaderboards
# ============================================================
print("9. REAL-WORLD: Different Leaderboards (Weekly/Monthly)")
print("-" * 70)

# Weekly leaderboard
weekly = "leaderboard:weekly"
r.zadd(weekly, {
    "ujjawal-singh": 500,
    "raj-singh": 480,
    "priya-sharma": 520
})

# Monthly leaderboard (cumulative)
monthly = "leaderboard:monthly"
r.zadd(monthly, {
    "ujjawal-singh": 2500,
    "raj-singh": 2200,
    "priya-sharma": 2800
})

print("Weekly Top 3:")
for rank, (player, score) in enumerate(r.zrevrange(weekly, 0, 2, withscores=True), 1):
    print(f"  {rank}. {player}: {int(score)}")

print("\nMonthly Top 3:")
for rank, (player, score) in enumerate(r.zrevrange(monthly, 0, 2, withscores=True), 1):
    print(f"  {rank}. {player}: {int(score)}")
print()

# ============================================================
# 10. REAL-WORLD: Rating System
# ============================================================
print("10. REAL-WORLD: Product Ratings")
print("-" * 70)

ratings = "ratings:products"
r.zadd(ratings, {
    "laptop": 4.8,
    "phone": 4.5,
    "tablet": 4.2,
    "monitor": 4.7,
    "keyboard": 4.3
})

print("Top-rated products:")
for rank, (product, rating) in enumerate(r.zrevrange(ratings, 0, 2, withscores=True), 1):
    print(f"  {rank}. {product}: {rating}/5.0")
print()

# ============================================================
# 11. REAL-WORLD: Most Viewed Posts
# ============================================================
print("11. REAL-WORLD: Most Viewed Posts")
print("-" * 70)

views = "views:posts:2024"
r.zadd(views, {
    "post:1": 5000,
    "post:2": 3200,
    "post:3": 8500,
    "post:4": 2100,
    "post:5": 6300
})

print("Top 3 most viewed posts:")
for rank, (post_id, view_count) in enumerate(r.zrevrange(views, 0, 2, withscores=True), 1):
    print(f"  {rank}. {post_id}: {int(view_count)} views")

print("\nPostition of post:2:")
rank = r.zrevrank(views, "post:2")
print(f"  Ranked #{rank + 1}")
print()

# ============================================================
# 12. REAL-WORLD: User Engagement Score
# ============================================================
print("12. REAL-WORLD: User Engagement Ranking")
print("-" * 70)

engagement = "engagement:2024"
r.zadd(engagement, {
    "ujjawal-singh": 95.5,
    "alice": 87.3,
    "bob": 92.1,
    "charlie": 85.0,
    "diana": 98.7
})

print("User engagement rankings:")
for rank, (user, score) in enumerate(r.zrevrange(engagement, 0, -1, withscores=True), 1):
    print(f"  {rank}. {user}: {score} points")
print()

# ============================================================
# 13. RANGE QUERIES
# ============================================================
print("13. RANGE QUERIES - Get Range by Rank")
print("-" * 70)

lb = "leaderboard:full"
r.zadd(lb, {f"player{i}": i*100 for i in range(1, 11)})

print("Bottom 3 players:")
for rank, (player, score) in enumerate(r.zrange(lb, 0, 2, withscores=True), 1):
    print(f"  {rank}. {player}: {int(score)}")

print("\nMiddle 3 players (ranks 5-7):")
for rank, (player, score) in enumerate(r.zrange(lb, 4, 6, withscores=True), 5):
    print(f"  {rank}. {player}: {int(score)}")
print()

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("SORTED SETS - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Add/Remove:
  ZADD key score member        - Add with score
  ZREM key member              - Remove member

Query by Rank:
  ZRANGE key 0 -1              - Get all (low to high)
  ZREVRANGE key 0 -1           - Get all (high to low)
  ZRANGE key 0 9 WITHSCORES    - Get with scores

Query by Position:
  ZSCORE key member            - Get member's score
  ZRANK key member             - Get rank (low to high)
  ZREVRANK key member          - Get rank (high to low)
  ZCARD key                    - Count members

Modify:
  ZINCRBY key increment member - Increase score
  ZCOUNT key min max           - Count in range

Use Cases:
  [OK] Leaderboards
  [OK] Top N rankings
  [OK] Ratings & reviews
  [OK] Priority queues
  [OK] Time-based sorting
  [OK] User engagement scores
  [OK] Most viewed content
  [OK] Product popularity

Performance:
  [FAST] ZADD, ZREM, ZSCORE, ZRANK = O(log N)
  [MEDIUM] ZRANGE, ZREVRANGE = O(log N + M)
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Build a game leaderboard with 100 players
2. Create weekly and monthly leaderboards
3. Track product ratings and get top 10
4. Build blog post popularity ranking
5. Create user engagement scores
6. Track API endpoint usage (most used)
7. Build a real-time ranking system
8. Create skill-based user tiers
9. Track customer satisfaction scores
10. Build video view rankings

Challenge: Build complete ranking system:
  - Daily leaderboard
  - Weekly leaderboard
  - Monthly leaderboard
  - Get player rank in each
  - Show top 10 in each
  - Update scores realtime
  - Award badges based on rank

Modify the code and experiment!
""")
