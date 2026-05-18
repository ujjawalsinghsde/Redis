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
import json

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


# ============================================================
# PRACTICE: Solutions for Transactions
# ============================================================
print("="*70)
print("PRACTICE: Transactions Exercises")
print("="*70 + "\n")

# 1. Implement atomic counter increment
print("1. Atomic counter increment")
print("-" * 70)
counter_key = f"{user}:page-views"
r.delete(counter_key)

pipe = r.pipeline()
pipe.multi()
pipe.set(counter_key, 0)
pipe.incr(counter_key)
pipe.incr(counter_key)
pipe.incr(counter_key)
pipe.execute()

print("  Counter value:", r.get(counter_key))
print()

# 2. Build safe money transfer system
print("2. Safe money transfer system")
print("-" * 70)
alice_account = "account:alice"
bob_account = "account:bob"
r.set(alice_account, 1000)
r.set(bob_account, 500)

def safe_transfer(from_account, to_account, amount):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(from_account)
      balance = int(r.get(from_account))
      if balance < amount:
        pipe.unwatch()
        return False
      pipe.multi()
      pipe.decrby(from_account, amount)
      pipe.incrby(to_account, amount)
      pipe.execute()
      return True
    except redis.WatchError:
      continue

print("  Before transfer:", r.get(alice_account), r.get(bob_account))
print("  Transfer result:", safe_transfer(alice_account, bob_account, 200))
print("  After transfer:", r.get(alice_account), r.get(bob_account))
print()

# 3. Create atomic inventory update
print("3. Atomic inventory update")
print("-" * 70)
inventory_key = "inventory:laptop"
order_key = "order:5001"
r.hset(inventory_key, mapping={"stock": 50, "reserved": 0})
r.delete(order_key)

def reserve_inventory(product_key, order_id, quantity):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(product_key)
      current_stock = int(r.hget(product_key, "stock"))
      if current_stock < quantity:
        pipe.unwatch()
        return False
      pipe.multi()
      pipe.hincrby(product_key, "stock", -quantity)
      pipe.hincrby(product_key, "reserved", quantity)
      pipe.hset(f"order:{order_id}", mapping={"product": product_key, "quantity": quantity, "status": "reserved"})
      pipe.execute()
      return True
    except redis.WatchError:
      continue

print("  Inventory before:", r.hgetall(inventory_key))
print("  Reserve result:", reserve_inventory(inventory_key, "5001", 5))
print("  Inventory after:", r.hgetall(inventory_key))
print("  Order:", r.hgetall(order_key))
print()

# 4. Implement badge award system
print("4. Badge award system")
print("-" * 70)
badge_stats = f"{user}:badge-stats"
badge_store = f"{user}:badges"
r.hset(badge_stats, mapping={"posts": 9, "followers": 95})
r.delete(badge_store)
r.hset(badge_store, mapping={"10-posts": "false", "100-followers": "false"})

pipe = r.pipeline()
pipe.multi()
pipe.hincrby(badge_stats, "posts", 1)
pipe.hset(badge_store, "10-posts", "true")
pipe.lpush(f"{user}:notifications", "Badge unlocked: 10 Posts!")
pipe.execute()

print("  Stats:", r.hgetall(badge_stats))
print("  Badges:", r.hgetall(badge_store))
print("  Notifications:", r.lrange(f"{user}:notifications", 0, -1))
print()

# 5. Build atomic order processing
print("5. Atomic order processing")
print("-" * 70)
product_key = "product:1"
order_123 = "order:123"
r.hset(product_key, mapping={"name": "Laptop", "stock": 10})
r.delete(order_123)

def process_order(prod_key, order_id, quantity):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(prod_key)
      stock = int(r.hget(prod_key, "stock"))
      if stock < quantity:
        pipe.unwatch()
        return False
      pipe.multi()
      pipe.hincrby(prod_key, "stock", -quantity)
      pipe.hset(f"order:{order_id}", mapping={"product": prod_key, "quantity": quantity, "status": "completed"})
      pipe.execute()
      return True
    except redis.WatchError:
      continue

print("  Order result:", process_order(product_key, "123", 3))
print("  Product:", r.hgetall(product_key))
print("  Order:", r.hgetall(order_123))
print()

# 6. Create atomic statistics update
print("6. Atomic statistics update")
print("-" * 70)
stats_key = "stats:daily"
r.hset(stats_key, mapping={"visits": 1000, "signups": 50, "purchases": 25})

pipe = r.pipeline()
pipe.multi()
pipe.hincrby(stats_key, "visits", 100)
pipe.hincrby(stats_key, "signups", 5)
pipe.hincrby(stats_key, "purchases", 3)
pipe.hset(stats_key, "last-updated", str(time.time()))
pipe.execute()

print("  Stats:", r.hgetall(stats_key))
print()

# 7. Implement atomic user registration
print("7. Atomic user registration")
print("-" * 70)
registration_email = "newuser@example.com"
user_id = "user:2001"
registration_key = f"registration:{registration_email}"
r.delete(registration_key)
r.delete(user_id)

def register_user(email, uid, name):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(registration_key)
      if r.exists(registration_key):
        pipe.unwatch()
        return False
      pipe.multi()
      pipe.set(registration_key, uid)
      pipe.hset(uid, mapping={"name": name, "email": email, "status": "active"})
      pipe.execute()
      return True
    except redis.WatchError:
      continue

print("  Registration result:", register_user(registration_email, user_id, "New User"))
print("  Registration key:", r.get(registration_key))
print("  Profile:", r.hgetall(user_id))
print()

# 8. Build cart checkout (all-or-nothing)
print("8. Cart checkout (all-or-nothing)")
print("-" * 70)
cart_key = f"{user}:cart"
stock_key = "inventory:checkout"
order_log = "orders:checkout"
r.delete(cart_key, stock_key, order_log)
r.hset(cart_key, mapping={"laptop": 1, "mouse": 2})
r.hset(stock_key, mapping={"laptop": 2, "mouse": 5})

def checkout(cart_hash, inventory_hash, order_hash):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(cart_hash, inventory_hash)
      cart_items = r.hgetall(cart_hash)
      if not cart_items:
        pipe.unwatch()
        return False
      for item, qty_text in cart_items.items():
        qty = int(qty_text)
        if int(r.hget(inventory_hash, item) or 0) < qty:
          pipe.unwatch()
          return False
      pipe.multi()
      for item, qty_text in cart_items.items():
        qty = int(qty_text)
        pipe.hincrby(inventory_hash, item, -qty)
      pipe.hset(order_hash, mapping={"status": "paid", "items": str(cart_items)})
      pipe.delete(cart_hash)
      pipe.execute()
      return True
    except redis.WatchError:
      continue

print("  Checkout result:", checkout(cart_key, stock_key, order_log))
print("  Inventory after checkout:", r.hgetall(stock_key))
print("  Cart after checkout:", r.hgetall(cart_key))
print("  Order log:", r.hgetall(order_log))
print()

# 9. Create atomic point transfer system
print("9. Atomic point transfer system")
print("-" * 70)
points_alice = "points:alice"
points_bob = "points:bob"
r.set(points_alice, 100)
r.set(points_bob, 75)

def transfer_points(src, dst, points):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(src)
      if int(r.get(src)) < points:
        pipe.unwatch()
        return False
      pipe.multi()
      pipe.decrby(src, points)
      pipe.incrby(dst, points)
      pipe.execute()
      return True
    except redis.WatchError:
      continue

print("  Before:", r.get(points_alice), r.get(points_bob))
print("  Transfer result:", transfer_points(points_alice, points_bob, 30))
print("  After:", r.get(points_alice), r.get(points_bob))
print()

# 10. Implement atomic API call logging
print("10. Atomic API call logging")
print("-" * 70)
api_calls = "api:calls"
api_audit = "api:audit"
r.delete(api_calls, api_audit)
r.hset(api_calls, mapping={"total": 0, "success": 0, "fail": 0})

def log_api_call(endpoint, status):
  pipe = r.pipeline()
  pipe.multi()
  pipe.hincrby(api_calls, "total", 1)
  if status == "success":
    pipe.hincrby(api_calls, "success", 1)
  else:
    pipe.hincrby(api_calls, "fail", 1)
  pipe.lpush(api_audit, json.dumps({"endpoint": endpoint, "status": status, "ts": str(time.time())}))
  pipe.execute()

log_api_call("GET /users", "success")
log_api_call("POST /login", "success")
log_api_call("POST /orders", "fail")

print("  Call stats:", r.hgetall(api_calls))
print("  Audit log:", r.lrange(api_audit, 0, -1))
print()

# Challenge: complete banking system
print("CHALLENGE: Complete banking system")
print("-" * 70)
bank_a = "bank:alice"
bank_b = "bank:bob"
ledger = "bank:ledger"
disputes = "bank:disputes"
for key in (bank_a, bank_b, ledger, disputes):
  r.delete(key)

r.set(bank_a, 1000)
r.set(bank_b, 500)

def bank_transfer(from_account, to_account, amount, ref):
  pipe = r.pipeline()
  while True:
    try:
      pipe.watch(from_account)
      if int(r.get(from_account)) < amount:
        pipe.unwatch()
        return False
      pipe.multi()
      pipe.decrby(from_account, amount)
      pipe.incrby(to_account, amount)
      pipe.lpush(ledger, json.dumps({
        "ref": ref,
        "from": from_account,
        "to": to_account,
        "amount": amount,
        "ts": str(time.time())
      }))
      pipe.execute()
      return True
    except redis.WatchError:
      continue

def dispute_transaction(ref, reason):
  r.hset(disputes, ref, json.dumps({"reason": reason, "ts": str(time.time())}))

print("  Balances before:", r.get(bank_a), r.get(bank_b))
print("  Transfer 250:", bank_transfer(bank_a, bank_b, 250, "tx-001"))
print("  Balances after:", r.get(bank_a), r.get(bank_b))
print("  Ledger entries:", r.lrange(ledger, 0, -1))
dispute_transaction("tx-001", "customer requested review")
print("  Disputes:", r.hgetall(disputes))
print("  Prevent overdraft transfer 5000:", bank_transfer(bank_a, bank_b, 5000, "tx-002"))
print()

print("ALL TRANSACTIONS PRACTICE PROBLEMS COMPLETED")
print("="*70)
