"""
COURSE 8: TRANSACTIONS - ACID Operations
==========================================

THEORY:
Transactions execute multiple commands atomically.
Either all commands execute or none (all or nothing).

Key Concepts:
  - MULTI: Start transaction
  - EXEC: Execute all commands
  - DISCARD: Cancel transaction
  - WATCH: Optimize with CAS (Compare-And-Swap)
  - Atomic: not interrupted by other clients

Common Operations:

1. MULTI - Start Transaction
   MULTI

2. Command Queue
   SET key value
   INCR counter
   LPUSH list item

3. EXEC - Execute All
   EXEC

4. DISCARD - Cancel
   DISCARD

5. WATCH - Optimistic Locking
   WATCH key

6. UNWATCH - Remove Watch
   UNWATCH

Benefits:
  - No race conditions
  - Atomic operations
  - All or nothing
  - Better than locks

Limitations:
  - Can't abort mid-transaction
  - No rollback
  - Linear order
  - Lua scripting for complex logic
"""

import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("TRANSACTIONS - ACID with UJJAWAL SINGH")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. BASIC TRANSACTION
# ============================================================
print("1. BASIC TRANSACTION - MULTI/EXEC")
print("-" * 70)

# Start transaction
pipe = r.pipeline()
pipe.multi()

# Queue commands
pipe.set(f"{user}:name", "Ujjawal Singh")
pipe.set(f"{user}:email", "ujjawal@example.com")
pipe.incr(f"{user}:login-count")

# Execute all at once
results = pipe.execute()
print(f"Transaction executed: {len(results)} commands")
print(f"Results: {results}")
print(f"Name: {r.get(f'{user}:name')}")
print(f"Logins: {r.get(f'{user}:login-count')}\n")

# ============================================================
# 2. ATOMICITY - All or Nothing
# ============================================================
print("2. ATOMICITY - All Commands Execute or None")
print("-" * 70)

# Initialize values
r.set(f"{user}:balance", 1000)
r.set(f"{user}:transactions", 0)

print(f"Before transaction:")
print(f"  Balance: {r.get(f'{user}:balance')}")
print(f"  Transactions: {r.get(f'{user}:transactions')}")

# Money transfer transaction
pipe = r.pipeline()
pipe.multi()
pipe.decrby(f"{user}:balance", 100)  # Withdraw
pipe.incr(f"{user}:transactions")    # Count transaction
results = pipe.execute()

print(f"\nAfter transaction:")
print(f"  Balance: {r.get(f'{user}:balance')}")
print(f"  Transactions: {r.get(f'{user}:transactions')}\n")

# ============================================================
# 3. DISCARD - Cancel Transaction
# ============================================================
print("3. DISCARD - Cancel Transaction Before Execute")
print("-" * 70)

balance_before = int(r.get(f"{user}:balance"))

pipe = r.pipeline()
pipe.multi()
pipe.decrby(f"{user}:balance", 500)  # Try to withdraw
pipe.discard()  # Cancel!

print(f"Attempted to withdraw 500")
balance_after = int(r.get(f"{user}:balance"))
print(f"Balance before: {balance_before}")
print(f"Balance after: {balance_after} (unchanged!)\n")

# ============================================================
# 4. WATCH - Optimistic Locking
# ============================================================
print("4. WATCH - Detect Conflicts")
print("-" * 70)

r.set("product:stock", 10)

# Watch the key
pipe = r.pipeline()
pipe.watch("product:stock")

stock = int(r.get("product:stock"))
print(f"Current stock: {stock}")

# Simulate another client changing the stock
time.sleep(0.1)
r.decrby("product:stock", 2)
print(f"Another client sold 2 units")

# Try transaction - will fail!
try:
    pipe.multi()
    pipe.decrby("product:stock", 5)
    pipe.execute()
    print(f"Transaction succeeded")
except redis.WatchError:
    print(f"Transaction FAILED - watched key changed!")
    print(f"Current stock: {r.get('product:stock')}\n")

# ============================================================
# 5. REAL-WORLD: Money Transfer
# ============================================================
print("5. REAL-WORLD: Money Transfer (Atomic)")
print("-" * 70)

r.set("account:alice", 1000)
r.set("account:bob", 500)

print(f"Alice: ${r.get('account:alice')}")
print(f"Bob: ${r.get('account:bob')}")

# Transfer $200 from Alice to Bob
pipe = r.pipeline()
pipe.multi()
pipe.decrby("account:alice", 200)
pipe.incrby("account:bob", 200)
results = pipe.execute()

print(f"\nAfter transfer of $200:")
print(f"Alice: ${r.get('account:alice')}")
print(f"Bob: ${r.get('account:bob')}\n")

# ============================================================
# 6. REAL-WORLD: Inventory Update
# ============================================================
print("6. REAL-WORLD: Order Processing (Atomic)")
print("-" * 70)

r.hset("product:1", mapping={"name": "Laptop", "stock": 50})
r.hset("order:123", mapping={"product": "1", "quantity": 0})

stock = int(r.hget("product:1", "stock"))
print(f"Laptop stock before order: {stock}")

# Process order: update stock AND record in order
pipe = r.pipeline()
pipe.multi()
pipe.hincrby("product:1", "stock", -5)  # Sell 5 units
pipe.hset("order:123", "quantity", 5)    # Record order
pipe.hset("order:123", "status", "completed")
results = pipe.execute()

print(f"Laptop stock after order: {r.hget('product:1', 'stock')}")
print(f"Order status: {r.hget('order:123', 'status')}\n")

# ============================================================
# 7. REAL-WORLD: Statistics Update
# ============================================================
print("7. REAL-WORLD: Event Logging (Atomic)")
print("-" * 70)

r.hset("stats:daily", mapping={
    "visits": 1000,
    "signups": 50,
    "purchases": 25
})

print(f"Stats before:")
for key, val in r.hgetall("stats:daily").items():
    print(f"  {key}: {val}")

# Update multiple stats atomically
pipe = r.pipeline()
pipe.multi()
pipe.hincrby("stats:daily", "visits", 100)
pipe.hincrby("stats:daily", "signups", 5)
pipe.hincrby("stats:daily", "purchases", 3)
pipe.hset("stats:daily", "last-updated", str(time.time()))
results = pipe.execute()

print(f"\nStats after:")
for key, val in r.hgetall("stats:daily").items():
    print(f"  {key}: {val}")
print()

# ============================================================
# 8. REAL-WORLD: User Badge System
# ============================================================
print("8. REAL-WORLD: Award Badges (Atomic)")
print("-" * 70)

r.hset(f"{user}:badges", mapping={
    "first-login": "true",
    "10-posts": "false",
    "100-followers": "false"
})

r.hset(f"{user}:stats", mapping={
    "posts": 9,
    "followers": 95
})

# User creates new post (10th post)
pipe = r.pipeline()
pipe.multi()
pipe.hincrby(f"{user}:stats", "posts", 1)
post_count = 10

if post_count == 10:
    pipe.hset(f"{user}:badges", "10-posts", "true")
    pipe.lpush(f"{user}:notifications", "Badge unlocked: 10 Posts!")

results = pipe.execute()

print(f"Posts: {r.hget(f'{user}:stats', 'posts')}")
print(f"Badge (10-posts): {r.hget(f'{user}:badges', '10-posts')}")
print(f"Notifications: {r.lrange(f'{user}:notifications', 0, -1)}\n")

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("TRANSACTIONS - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Basic Transaction:
  pipe = r.pipeline()      - Create pipeline
  pipe.multi()             - Start transaction
  pipe.set/incr/...        - Queue commands
  pipe.execute()           - Execute all

Monitoring:
  WATCH key                - Watch key for changes
  UNWATCH                  - Remove watches

Cancel:
  DISCARD                  - Cancel transaction

Use Cases:
  [OK] Money transfers
  [OK] Inventory updates
  [OK] Order processing
  [OK] Counter increments
  [OK] Statistics updates
  [OK] Badge awarding
  [OK] Multi-step operations
  [OK] Prevent race conditions

Benefits:
  [OK] Atomicity (all or nothing)
  [OK] No race conditions
  [OK] Consistent state
  [OK] No manual locks needed

Limitations:
  [NO] No rollback
  [NO] No COMMIT/ABORT like SQL
  [NO] Can't abort mid-transaction
  [NO] Complex logic needs Lua scripts
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Implement atomic counter increment
2. Build safe money transfer system
3. Create atomic inventory update
4. Implement badge award system
5. Build atomic order processing
6. Create atomic statistics update
7. Implement atomic user registration
8. Build cart checkout (all-or-nothing)
9. Create atomic point transfer system
10. Implement atomic API call logging

Challenge: Build complete banking system:
  - Atomic transfers between accounts
  - Transaction logging
  - Balance consistency
  - Dispute resolution
  - Prevent overdrafts
  - Audit trail

Modify the code and experiment!
""")
