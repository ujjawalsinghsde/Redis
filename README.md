# REDIS

---

## ALL 12 COURSES

| # | Course | File | Focus Area |
|---|--------|------|-----------|
| 1 | Foundations | course_01_foundations.py | What & Why Redis |
| 2 | Strings | course_02_strings.py | Counters, Caching, Locks |
| 3 | Lists | course_03_lists.py | Queues, Feeds |
| 4 | Sets | course_04_sets.py | Tags, Unique Items |
| 5 | Hashes | course_05_hashes.py | Objects, Profiles |
| 6 | Sorted Sets | course_06_sorted_sets.py | Leaderboards, Rankings |
| 7 | Expiration | course_07_expiration.py | TTL, Auto-Cleanup |
| 8 | Transactions | course_08_transactions.py | ACID, Atomic Ops |
| 9 | Pub/Sub | course_09_pubsub.py | Real-Time Messaging |
| 10 | Persistence | course_10_persistence.py | RDB, AOF, Backup |
| 11 | Caching | course_11_caching.py | Cache Patterns |
| 12 | Sessions/Rate/Queues | course_12_sessions.py | Production Patterns |

**Run them in order:** `python course_01_foundations.py` → `course_12_sessions.py`

---

## TABLE OF CONTENTS

1. [All 12 Courses](#all-12-courses)
2. [Quick Start](#quick-start)
3. [Learning Path](#learning-path)
4. [What You'll Learn](#what-youll-learn)
5. [Commands Reference](#commands-reference)
6. [Production Checklist](#production-checklist)

---

## QUICK START

**Do this RIGHT NOW:**

```bash
# Step 1: Verify Redis is running
docker compose up -d
docker compose ps

# Step 2: Run your first course
python course_01_foundations.py

# Step 3: Modify the code and run again
```

---

## LEARNING PATH

### PHASE 1: FOUNDATIONS & BASIC DATA TYPES

**Foundations**
```bash
python course_01_foundations.py
```
Learn:
- What Redis is (in-memory data store)
- Why it's fast (100,000+ ops/sec)
- When to use/NOT use
- Core concepts (keys, values, expiration)
- Real-world examples

**Strings - Counters & Caching**
```bash
python course_02_strings.py
```
Learn:
- SET/GET operations
- INCR/DECR counters
- SETEX expiration
- Real patterns: rate limiting, distributed locks
- Cache JSON objects
- Performance optimization

**Lists - Queues & Feeds**
```bash
python course_03_lists.py
```
Learn:
- LPUSH/RPUSH/LPOP/RPOP operations
- Task queues (producer-consumer pattern)
- Activity feeds & notifications
- Priority queues
- Message buffers

### PHASE 2: ALL DATA TYPES

**Sets - Tags & Unique Items**
```bash
python course_04_sets.py
```
Learn:
- SADD/SMEMBERS/SISMEMBER
- Set intersections & unions
- Unique visitor tracking
- Friend suggestions
- Spam detection patterns

**Hashes - Objects & Profiles**
```bash
python course_05_hashes.py
```
Learn:
- HSET/HGET/HGETALL
- User profile storage
- Product information
- Session data
- Settings & configuration

**Sorted Sets - Leaderboards**
```bash
python course_06_sorted_sets.py
```
Learn:
- ZADD/ZRANGE/ZREVRANGE
- Leaderboards & rankings
- Top N queries
- Scoring systems
- Time-based sorting

### PHASE 3: ADVANCED FEATURES

**Expiration & TTL - Auto-Cleanup**
```bash
python course_07_expiration.py
```
Learn:
- EXPIRE/TTL commands
- SETEX pattern
- Session management
- OTP expiration
- Cache invalidation
- Automatic cleanup

**Transactions - ACID Operations**
```bash
python course_08_transactions.py
```
Learn:
- MULTI/EXEC/DISCARD
- Atomic operations
- WATCH for optimistic locking
- Money transfers
- Inventory updates
- All-or-nothing execution

**Pub/Sub - Real-Time Messaging**
```bash
python course_09_pubsub.py
```
Learn:
- PUBLISH/SUBSCRIBE
- Real-time notifications
- Chat systems
- Live updates
- Event broadcasting
- WebSocket integration

### PHASE 4: PERSISTENCE & PRODUCTION

**Persistence - RDB & AOF**
```bash
python course_10_persistence.py
```
Learn:
- RDB snapshots
- AOF (Append Only File)
- Backup strategies
- Recovery procedures
- Disaster recovery
- Data durability

**Caching Patterns**
```bash
python course_11_caching.py
```
Learn:
- Cache-aside pattern
- Write-through caching
- Write-behind pattern
- Cache invalidation strategies
- Cache versioning
- Performance metrics

### PHASE 5: PRODUCTION PATTERNS

**Sessions, Rate Limiting & Queues**
```bash
python course_12_sessions.py
```
Learn:
- Session management
- User login & logout
- Remember-me tokens
- Rate limiting algorithms
- Token bucket pattern
- Task queue management
- Worker pattern

---

## WHAT YOU'LL LEARN

### ALL 5 DATA TYPES

**1. STRINGS** - Counters, caching, tokens
```python
r.set('key', 'value')      # Store
r.incr('counter')          # Increment
r.setex('temp', 60, 'val') # With expiration
```
✅ Course 2 - Complete coverage with 14 practical examples

**2. LISTS** - Queues, feeds, notifications
```python
r.lpush('queue', 'item')   # Add to front
r.rpop('queue')            # Remove from back
r.lrange('queue', 0, -1)   # Get all
```
✅ Course 3 - Task queues, activity feeds, notifications

**3. SETS** - Unique items, tags, intersections
```python
r.sadd('tags', 'python', 'redis')     # Add
r.smembers('tags')                    # Get all
r.sinter('tags1', 'tags2')            # Intersection
```
✅ Course 4 - Friend suggestions, voting, deduplication

**4. HASHES** - Objects, user profiles
```python
r.hset('user:1', mapping={'name': 'Ujjawal', 'age': 25})
r.hgetall('user:1')  # Get all fields
```
✅ Course 5 - Profiles, settings, form storage

**5. SORTED SETS** - Leaderboards, rankings
```python
r.zadd('leaderboard', {'ujjawal': 100, 'alice': 90})
r.zrevrange('leaderboard', 0, 9)  # Top 10
```
✅ Course 6 - Leaderboards, ratings, top N queries

### ADVANCED FEATURES

✅ Course 7 - **Expiration & TTL**
- Auto-expiring keys
- Session management
- OTP verification
- Cache invalidation

✅ Course 8 - **Transactions**
- ACID operations
- Atomic updates
- Money transfers
- Optimistic locking

✅ Course 9 - **Pub/Sub**
- Real-time messaging
- Chat systems
- Live updates
- Event broadcasting

✅ Course 10 - **Persistence**
- RDB snapshots
- AOF logging
- Backup & recovery
- Data durability

✅ Course 11 - **Caching**
- Cache-aside pattern
- Write-through caching
- Invalidation strategies
- Performance metrics

✅ Course 12 - **Production**
- Session management
- Rate limiting
- Task queues
- Job processing

### PRODUCTION PATTERNS

1. **Caching** - Speed up applications 100x
2. **Rate Limiting** - Protect APIs from abuse
3. **Task Queues** - Process jobs asynchronously
4. **Session Store** - Manage user logins
5. **Leaderboards** - Track rankings
6. **Pub/Sub** - Real-time messaging
7. **Distributed Locks** - Prevent race conditions
8. **Analytics** - Count & track metrics
9. **Activity Feeds** - Recent posts/actions
10. **Notifications** - Real-time alerts
11. **Message Buffers** - Temporary storage
12. **Transactions** - ACID operations
13. **Persistence** - Backup & restore
14. **High Availability** - Master-slave setup
15. **Monitoring** - Performance tracking

---

## COMMANDS REFERENCE

### STRING COMMANDS
```python
r.set(key, value)              # Store value
r.get(key)                     # Retrieve value
r.incr(key)                    # Increment number by 1
r.incrby(key, 5)               # Increment by 5
r.decr(key)                    # Decrement by 1
r.setex(key, 60, value)        # Set with expiration
r.mset({'k1': 'v1', 'k2': 'v2'})  # Multiple set
r.mget(['k1', 'k2'])           # Multiple get
```

### LIST COMMANDS
```python
r.lpush(key, value)            # Add to left
r.rpush(key, value)            # Add to right
r.lpop(key)                    # Remove from left
r.rpop(key)                    # Remove from right
r.llen(key)                    # Get length
r.lrange(key, 0, -1)           # Get all items
r.ltrim(key, 0, 99)            # Keep first 100, delete rest
r.lindex(key, 0)               # Get by index
```

### SET COMMANDS
```python
r.sadd(key, member)            # Add member
r.smembers(key)                # Get all members
r.sismember(key, member)       # Check membership
r.srem(key, member)            # Remove member
r.scard(key)                   # Get size
r.sinter(key1, key2)           # Intersection
r.sunion(key1, key2)           # Union
```

### HASH COMMANDS
```python
r.hset(key, mapping={...})     # Set fields
r.hget(key, field)             # Get single field
r.hgetall(key)                 # Get all fields
r.hincrby(key, field, 1)       # Increment field
r.hdel(key, field)             # Delete field
r.hexists(key, field)          # Check field exists
```

### SORTED SET COMMANDS
```python
r.zadd(key, {'member': score})         # Add with score
r.zrange(key, 0, -1)                   # Get by rank
r.zrevrange(key, 0, 9)                 # Top 10
r.zscore(key, member)                  # Get score
r.zrank(key, member)                   # Get rank
r.zcard(key)                           # Get size
```

### KEY MANAGEMENT
```python
r.keys('*')                    # Get all keys
r.delete(key)                  # Delete key
r.expire(key, 60)              # Set expiration
r.ttl(key)                     # Get time to live
r.type(key)                    # Get data type
r.exists(key)                  # Check if exists
r.flushdb()                    # Clear database
```

---

## TROUBLESHOOTING

### Error: "Connection refused"
```bash
docker-compose up -d  # Start Redis
```

### Error: "WRONGTYPE Operation"
```python
r.type(key)  # Check the key type first
```

### Error: "Out of Memory"
```python
r.config_set('maxmemory', '4gb')
r.config_set('maxmemory-policy', 'allkeys-lru')
```

### Slow Queries
```python
# Enable slow log
r.config_set('slowlog-log-slower-than', 10000)

# View slow queries
for entry in r.slowlog_get():
    print(entry)
```
