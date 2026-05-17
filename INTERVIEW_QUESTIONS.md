# Redis Interview Questions

---

## Q1: What's the difference between Redis and Memcached?

### Redis
- ✅ Rich data types (strings, lists, sets, hashes, sorted sets)
- ✅ Persistence (RDB, AOF)
- ✅ Transactions (MULTI/EXEC)
- ✅ Pub/Sub messaging
- ✅ Lua scripting
- ✅ Replication & Clustering
- ❌ More memory usage
- ❌ Single-threaded (can be bottleneck)

### Memcached
- ✅ Simpler (strings only)
- ✅ Lower memory overhead
- ✅ Multi-threaded
- ❌ No persistence
- ❌ No transactions
- ❌ No pub/sub
- ❌ No scripting

### When to Use
- **Redis**: Complex operations, data types, persistence needed
- **Memcached**: Simple caching, speed critical, distributed setup

### Conclusion
Redis is more powerful. Memcached is simpler & lighter. Most modern projects use Redis.

---

## Q2: How do you implement rate limiting?

### Approach: Token Bucket Algorithm

```python
import redis

def rate_limit(user_id, limit=10, window=60):
    key = f'rate:{user_id}'

    # Increment counter
    count = r.incr(key)

    # Set expiration on first request
    if count == 1:
        r.expire(key, window)

    # Check if exceeded limit
    return count <= limit

# Usage
if not rate_limit(user_id, limit=100, window=3600):
    return "Rate limit exceeded"
```

### Variations
1. **Token Bucket**: Fixed capacity, fills over time
2. **Sliding Window**: Count requests in moving window
3. **Per-Endpoint**: Different limits for different endpoints
4. **User Tiers**: Different limits for different subscription tiers

### Advanced Pattern (Sliding Window)
```python
def sliding_window_limit(user_id, limit=100, window=3600):
    key = f'rate:{user_id}'
    now = time.time()

    # Remove old entries outside window
    r.zremrangebyscore(key, 0, now - window)

    # Count requests in window
    count = r.zcard(key)

    if count < limit:
        r.zadd(key, {now: now})
        r.expire(key, window)
        return True
    return False
```

### Production Example
```python
# API tier limits
limits = {
    'free': 100,        # per hour
    'pro': 1000,        # per hour
    'enterprise': -1    # unlimited
}

user_tier = get_user_tier(user_id)
limit = limits[user_tier]

if not rate_limit(user_id, limit=limit):
    return 429, "Rate limited"
```

---

## Q3: How do you handle cache invalidation?

### Problem
Stale data in cache - real data changed but cache still old

### Strategies

#### 1. TTL (Time To Live) - Most Common
```python
r.setex('cache:key', 300, data)  # Expires in 5 min
```
- **Pros**: Simple, automatic cleanup
- **Cons**: Might return stale data briefly

#### 2. Event-Based Invalidation
```python
# When data changes, delete cache
r.delete('cache:user:123')
```
- **Pros**: Fresh data immediately
- **Cons**: Need to track all cache dependencies

#### 3. Cache Tags - Group Related Caches
```python
# Store cache with tags
r.set('cache:profile:123', profile_data)
r.sadd('tags:user:123', 'profile')

# Invalidate all related caches
tags = r.smembers('tags:user:123')
for tag in tags:
    r.delete(f'cache:{tag}:123')
```

#### 4. Cache Versioning - Create New Key
```python
# Old version
r.set('config:v1', config_data)

# New version invalidates old
r.set('config:v2', new_config_data)
r.delete('config:v1')
```

#### 5. Cache Warming - Proactive Refresh
```python
# Refresh cache before expiration
if r.ttl('cache:key') < 60:
    refresh_cache('key')
```

### Best Practice - Hybrid Approach
1. Use TTL for auto-cleanup (prevent memory bloat)
2. Use event-based for critical updates (delete on change)
3. Monitor hit rate to adjust TTL

### Example - User Profile Cache
```python
def get_user(user_id):
    cache_key = f'user:{user_id}'

    # Try cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss
    user = fetch_from_db(user_id)
    r.setex(cache_key, 3600, json.dumps(user))
    return user

def update_user(user_id, data):
    update_db(user_id, data)
    r.delete(f'user:{user_id}')  # Invalidate cache
```

---

## Q4: What happens if Redis runs out of memory?

### Problem
Redis is in-memory. When full, what happens?

### Eviction Policies

| Policy | Behavior | Best For |
|--------|----------|----------|
| **allkeys-lru** | Evict LRU keys | General caching |
| **volatile-lru** | Evict LRU with TTL | Safe & efficient |
| **allkeys-lfu** | Evict LFU keys | Working sets |
| **volatile-lfu** | Evict LFU with TTL | Time-based data |
| **allkeys-random** | Random eviction | Fast but risky |
| **volatile-random** | Random with TTL | Medium safety |
| **volatile-ttl** | Evict shortest TTL | Time-sensitive data |
| **noeviction** | Return error | Safe but crashes |

### Configuration

```conf
# redis.conf
maxmemory 2gb                       # Set max memory
maxmemory-policy allkeys-lru        # Set policy
```

### Python Configuration
```python
r.config_set('maxmemory', '2gb')
r.config_set('maxmemory-policy', 'allkeys-lru')
```

### Monitoring
```python
# Check memory usage
info = r.info('memory')
used = info['used_memory']
max_mem = info['maxmemory']
percentage = (used / max_mem) * 100
```

### Best Practices
1. Set maxmemory appropriately
2. Use TTL on temporary data
3. Monitor memory usage
4. Choose right eviction policy
5. Have alerts at 80% usage
6. Plan capacity (data size × 3 for safety)

---

## Q5: How do transactions work in Redis?

### Basic Transaction
```python
pipe = r.pipeline()
pipe.multi()              # Start transaction
pipe.set('key1', 'val1')
pipe.incr('counter')
pipe.lpush('list', 'item')
results = pipe.execute()  # Execute all or none
```

### Why Transactions?
- Prevent race conditions
- Ensure data consistency
- Atomic operations (not interrupted)

### Example - Money Transfer
```python
def transfer_money(from_account, to_account, amount):
    pipe = r.pipeline()
    pipe.multi()

    # Debit from account
    pipe.decrby(f'account:{from_account}', amount)

    # Credit to account
    pipe.incrby(f'account:{to_account}', amount)

    # Log transaction
    pipe.lpush('transactions', {
        'from': from_account,
        'to': to_account,
        'amount': amount
    })

    # Execute - all or none
    try:
        results = pipe.execute()
        return True
    except redis.WatchError:
        return False
```

### WATCH - Optimistic Locking
```python
def buy_product(user_id, product_id):
    stock_key = f'product:{product_id}:stock'

    # Watch the key
    pipe = r.pipeline()
    pipe.watch(stock_key)

    stock = int(r.get(stock_key))
    if stock > 0:
        pipe.multi()
        pipe.decrby(stock_key, 1)
        pipe.sadd(f'user:{user_id}:purchases', product_id)
        results = pipe.execute()
        return True
    else:
        pipe.unwatch()
        return False
```

### Difference vs SQL

| Aspect | Redis | SQL |
|--------|-------|-----|
| Rollback | No | Yes |
| Nested transactions | No | Yes |
| COMMIT/ABORT | No | Yes |

### When to Use
- ✅ Simple multi-step operations
- ✅ Counters with consistency needs
- ✅ Atomic updates
- ✅ Prevent race conditions
- ❌ Complex business logic
- ❌ Need rollback
- ❌ Conditional logic (use Lua scripts)

---

## Q6: How do you implement high availability?

### Strategy 1: Master-Slave Replication
```
Master (writes) → Slave 1 (reads)
               → Slave 2 (reads)
               → Slave 3 (reads)
```

**Setup on slave:**
```conf
replicaof master.server 6379
```

### Strategy 2: Redis Sentinel (Recommended)
```
Sentinel 1 \
Sentinel 2  -- Monitor --> Master/Slaves
Sentinel 3 /
```

**Failover Process:**
1. Sentinel detects master down
2. Quorum votes on failover
3. Slave promoted to master
4. Other slaves repoint to new master
5. Applications reconnect

### Strategy 3: Redis Cluster (Distributed)
```
Slot 0-5000:   Node A + Slave A
Slot 5001-10k: Node B + Slave B
Slot 10k-16k:  Node C + Slave C
```

### Production HA Setup
- 3 Master nodes (minimum)
- 3 Slave nodes (one per master)
- 3-5 Sentinel nodes
- Different data centers if possible
- Load balancer in front

### Monitoring
```python
# Check replication status
info = r.info('replication')
print(info['role'])                    # master or slave
print(info['connected_slaves'])
print(info['master_repl_offset'])
```

### Failover Test
1. Kill master instance
2. Verify sentinel promotes slave
3. Check client reconnections
4. Verify data consistency

---

## Q7: What's the N+1 query problem and how does Redis help?

### The Problem

**Bad Code:**
```python
users = db.query("SELECT * FROM users LIMIT 100")  # 1 query

for user in users:
    posts = db.query(f"SELECT * FROM posts WHERE user_id = {user.id}")
    # N more queries!

# Total: 1 + 100 = 101 queries!
```

### Why It's Slow
- Each DB query takes time
- Network latency
- Database overhead
- Becomes exponential with data

### Solution 1: Use JOIN (SQL)
```sql
SELECT users.*, posts.*
FROM users
LEFT JOIN posts ON users.id = posts.user_id
-- Much faster!
```

### Solution 2: Cache with Redis
```python
# Get users
users = db.query("SELECT * FROM users LIMIT 100")

for user in users:
    cache_key = f"posts:{user.id}"

    # Check Redis cache
    posts = r.get(cache_key)
    if posts:
        user.posts = json.loads(posts)  # From cache
    else:
        posts = db.query(...)           # From DB
        r.setex(cache_key, 3600, json.dumps(posts))
        user.posts = posts

# Reduces DB queries significantly!
```

### Redis Patterns

#### 1. Cache-Aside
```python
def get_user_posts(user_id):
    cache_key = f'posts:{user_id}'
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    posts = db.query(f"SELECT * FROM posts WHERE user_id = {user_id}")
    r.setex(cache_key, 3600, json.dumps(posts))
    return posts
```

#### 2. Batch Loading
```python
# Load all data at once
posts = db.query("SELECT * FROM posts WHERE user_id IN (...)")

# Cache each
for post in posts:
    r.set(f'post:{post.id}', json.dumps(post))
```

#### 3. Denormalization
```python
# Store user with posts count
r.hset(f'user:{user_id}', mapping={
    'name': user.name,
    'post_count': len(user.posts)
})
# No need to query posts table!
```

### Performance Impact
```
Without Redis:
  100 users × 100 posts = 101 queries = 101 DB calls

With Redis:
  100 users × 100 posts = 101 Redis calls (if cached)
  Redis call: < 1ms
  DB query: 10-100ms

  Speedup: 10-100x faster!
```

---

## Q8: How do you backup and restore Redis?

### Backup Strategy 1: RDB (Redis Database)
- Binary format
- Compact
- Fast to load
- Point-in-time backups

**Manual Backup:**
```bash
redis-cli BGSAVE  # Background save
cp /var/lib/redis/dump.rdb /backups/dump-$(date +%s).rdb
```

**Auto Backup (redis.conf):**
```conf
save 900 1         # Snapshot every 900s if 1+ change
save 300 10        # Or every 300s if 10+ changes
```

### Backup Strategy 2: AOF (Append Only File)
- Text format
- Every write recorded
- More durable
- Larger file size

**Enable AOF:**
```conf
appendonly yes
appendfsync everysec
```

### Backup Strategy 3: Replication
- Slave has copy of data
- Automatic sync
- Good for HA

### Restore Process

**From RDB:**
```bash
1. Stop Redis:
   redis-cli SHUTDOWN

2. Copy backup:
   cp /backups/dump-12345.rdb /var/lib/redis/dump.rdb

3. Start Redis:
   redis-server

4. Data auto-loaded
```

**From AOF:**
```
1. AOF auto-loaded if appendonly yes
2. Redis replays all commands
```

### Backup Script
```bash
#!/bin/bash

# Create backup
redis-cli BGSAVE

# Wait for save to complete
while [ "$(redis-cli LASTSAVE)" == "$LASTSAVE" ]; do
    sleep 1
done

# Copy backup
cp /var/lib/redis/dump.rdb /backups/dump-$(date +%Y%m%d-%H%M%S).rdb

# Upload to cloud
aws s3 cp /backups/dump-*.rdb s3://my-backups/redis/

# Keep only last 7 days
find /backups -name "dump-*.rdb" -mtime +7 -delete
```

### Cron Job
```bash
# Daily backup at 2 AM
0 2 * * * /scripts/backup-redis.sh
```

### Production Best Practices
1. Daily backups (multiple copies)
2. Test restore regularly
3. Keep backups in 3 locations
4. Monitor backup size
5. Use replication for HA
6. Enable AOF for safety
7. Document recovery procedure

---

## Q9: How do you implement distributed locking?

### Simple Approach (NOT Reliable)
```python
def acquire_lock(resource):
    return r.setnx(f'lock:{resource}', 'locked')

def release_lock(resource):
    r.delete(f'lock:{resource}')

# Problem: What if process crashes before release?
```

### Better Approach - SETNX with Expiration
```python
def acquire_lock(resource, timeout=10):
    return r.setnx(f'lock:{resource}', 'locked')
    r.expire(f'lock:{resource}', timeout)

# Problem: Two operations not atomic!
```

### Best Approach - Atomic SET
```python
def acquire_lock(resource, timeout=10):
    return r.set(f'lock:{resource}', 'locked',
                 nx=True, ex=timeout)

def release_lock(resource):
    r.delete(f'lock:{resource}')
```

### Production Approach - Redlock
```python
from redlock import Redlock

dlm = Redlock([
    {"host": "localhost", "port": 6379, "db": 0},
    {"host": "localhost", "port": 6380, "db": 0},
    {"host": "localhost", "port": 6381, "db": 0}
])

# Try to acquire lock
lock = dlm.lock("resource", 1000)

if lock:
    try:
        # Do critical work
        critical_work()
    finally:
        dlm.unlock(lock)
else:
    print("Failed to acquire lock")
```

### Example - Critical Section
```python
def process_payment(transaction_id):
    lock_key = f'payment:{transaction_id}'

    if not r.set(lock_key, 'processing', nx=True, ex=30):
        return "Payment already processing"

    try:
        # Only one process can do this
        charge_card()
        update_database()
        send_confirmation()
        return "Success"
    finally:
        r.delete(lock_key)
```

### Race Condition WITHOUT Lock
```
Process 1: Check if payment processed - NO
Process 2: Check if payment processed - NO
Process 1: Charge card
Process 2: Charge card  <-- DOUBLE CHARGE!
```

### Race Condition WITH Lock
```
Process 1: Acquire lock - SUCCESS
Process 2: Acquire lock - FAIL (Process 1 holds it)
Process 1: Charge card
Process 1: Release lock
Process 2: Acquire lock - SUCCESS
Process 2: Check if charged - YES, SKIP
```

### Best Practices
1. Always set expiration (prevent deadlock)
2. Use atomic set operation (SET with NX/EX)
3. Keep critical section short
4. Use try/finally to ensure release
5. Use Redlock for multi-node systems
6. Monitor lock contention
7. Have fallback strategy

---

## Q10: What are common Redis performance issues?

### Issue 1: Memory Leaks / High Memory Usage

**Problem:**
- Keys not expiring
- Unbounded data structures
- Memory keeps growing

**Solutions:**
```python
# Set TTL on all keys
r.setex('cache:key', 3600, data)

# Monitor memory
info = r.info('memory')
print(f"Memory: {info['used_memory_human']}")

# Set maxmemory
r.config_set('maxmemory', '2gb')
```

### Issue 2: Slow Queries

**Problem:**
- KEYS command (scans all keys)
- Large LRANGE/SMEMBERS
- Nested operations

**Solutions:**
```python
# Use SCAN instead of KEYS
cursor = 0
while True:
    cursor, keys = r.scan(cursor)
    if cursor == 0:
        break

# Use LTRIM to limit list size
r.ltrim('list', 0, 99)

# Use pipelining
pipe = r.pipeline()
for key in keys:
    pipe.get(key)
results = pipe.execute()
```

### Issue 3: Blocking Operations

**Problem:**
- BLPOP blocking forever
- Stuck connections
- Slow client hanging

**Solution:**
```python
# Set timeout
result = r.blpop('queue', timeout=5)
```

### Issue 4: Wrong Data Type Usage

**Problem:**
- String for large list (should be LIST)
- HASH for many fields (consider splitting)
- SET with millions of items

**Solution:**
```python
# Right data structure for each use case
# Profile and optimize
```

### Issue 5: No Pipelining

**Problem:**
```python
# Slow - 100 separate calls
for i in range(100):
    r.set(f'key:{i}', i)
```

**Solution:**
```python
# Fast - one round trip
pipe = r.pipeline()
for i in range(100):
    pipe.set(f'key:{i}', i)
pipe.execute()
```

### Issue 6: Eviction Thrashing

**Problem:**
- Keys constantly evicted
- Low hit rate
- Performance degradation

**Solution:**
```python
# Monitor hit rate
info = r.info('stats')
hits = info['keyspace_hits']
misses = info['keyspace_misses']
hit_rate = hits / (hits + misses) * 100

# Increase memory if below 90% hit rate
```

### Monitoring & Debugging

**Check slow queries:**
```python
r.config_set('slowlog-log-slower-than', 10000)  # 10ms
slowlog = r.slowlog_get()
for entry in slowlog:
    print(f"{entry['command']}: {entry['duration']}us")
```

**Check memory:**
```python
info = r.info('memory')
print(f"Used: {info['used_memory_human']}")
print(f"Peak: {info['used_memory_peak_human']}")
```

**Find big keys:**
```bash
redis-cli --bigkeys
```

---

## Q11: What's the difference between Kafka and Redis?

### Redis
- ✅ In-memory, ultra-fast (microseconds)
- ✅ Rich data types (strings, lists, hashes, sets, sorted sets)
- ✅ Transactions (MULTI/EXEC)
- ✅ Pub/Sub (real-time, memory-based)
- ✅ Persistence (RDB, AOF) - optional
- ✅ Low latency, great for caching
- ❌ Limited retention (memory-bound)
- ❌ Not designed for high-volume streaming
- ❌ Single-threaded core

### Kafka
- ✅ Distributed, fault-tolerant messaging broker
- ✅ High throughput (millions msgs/sec)
- ✅ Persistent storage (disk-based, configurable retention)
- ✅ Consumer groups (parallel processing)
- ✅ Replayability (messages retained)
- ✅ Exactly-once semantics available
- ✅ Designed for event streaming
- ❌ Higher latency (milliseconds vs microseconds)
- ❌ More complex to operate
- ❌ Overkill for simple caching

### Comparison Table

| Aspect | Redis | Kafka |
|--------|-------|-------|
| **Storage** | In-memory | Disk-based |
| **Latency** | Microseconds | Milliseconds |
| **Throughput** | High | Very High (millions msgs) |
| **Retention** | Temporary (TTL) | Permanent (configurable) |
| **Use Case** | Caching, Sessions, Real-time | Event Streaming, Logging |
| **Replayability** | No | Yes (messages replayed) |
| **Consumer Groups** | No | Yes (parallel consumption) |
| **Persistence** | Optional | Built-in |
| **Data Loss Risk** | Higher | Lower |
| **Setup Complexity** | Simple | Complex |

### When to Use

**Use Redis when:**
- ✅ Need sub-millisecond latency
- ✅ Caching layer required
- ✅ Session storage
- ✅ Real-time leaderboards, counters
- ✅ Pub/Sub for immediate notifications
- ✅ Rate limiting, queues
- ✅ Simple architecture, fast setup

**Use Kafka when:**
- ✅ High-volume event streaming
- ✅ Need message replay/reprocessing
- ✅ Multiple consumers needed (consumer groups)
- ✅ Long-term data retention required
- ✅ Building audit logs, event sourcing
- ✅ Decoupled systems communication
- ✅ Guaranteed message delivery
- ✅ Complex data pipelines

### Real-World Example

```
E-Commerce Platform:

Redis:
  - Product cache (fast lookups)
  - Session store (user login)
  - Shopping cart (temporary)
  - Real-time notifications
  - Rate limiting (API calls)

Kafka:
  - Order events → persisted stream
  - User activity logging
  - Analytics pipeline
  - Order → Warehouse → Shipping
  - Multiple services consume order events
```

### Hybrid Approach

Many systems use BOTH:

```
User Action
    ↓
[Kafka] ← Event published
    ↓
[Consumers] ← Order service, Analytics, Notification service
    ↓
[Redis] ← Cache result, store session, send real-time notification
```

**Why?**
- Kafka: Reliable, persistent event backbone
- Redis: Fast access, real-time response

### Production Decision Tree

```
High throughput streaming? → YES → Use Kafka
                            → NO → Continue

Need message replay? → YES → Use Kafka
                      → NO → Continue

Multiple consumers needed? → YES → Use Kafka
                            → NO → Continue

Sub-millisecond latency? → YES → Use Redis
                          → NO → Continue

Just caching/sessions? → YES → Use Redis
                        → NO → Both or neither
```

---

## Interview Tips

### Common Follow-Ups
1. "How would you scale this?" → Clustering, Sentinel, Replication
2. "What about data loss?" → RDB, AOF, Replication
3. "How would you monitor?" → Memory, slowlog, hit rate
4. "What are the limitations?" → Single-threaded, memory-bounded
5. "What if Redis goes down?" → HA setup, fallback, persistence

### Key Talking Points
- Speed (100x faster than DB)
- Simplicity (easy to understand)
- Versatility (5 data types)
- Scalability (clustering)
- Reliability (persistence)
- Operations (monitoring)

### Mistakes to Avoid
- ✗ Treating Redis as database
- ✗ No TTL on keys (memory bloat)
- ✗ Caching stale data forever
- ✗ Using wrong data types
- ✗ No monitoring
- ✗ Single point of failure
- ✗ Ignoring persistence

### Things to Emphasize
- ✓ Know when to use Redis
- ✓ Know when NOT to use it
- ✓ Production concerns (HA, persistence)
- ✓ Performance optimization
- ✓ Data structure optimization
- ✓ Monitoring & debugging
- ✓ Cost & resource management
