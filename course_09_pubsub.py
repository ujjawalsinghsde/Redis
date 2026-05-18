"""
COURSE 9: PUB/SUB - Real-Time Messaging
========================================

THEORY:
Publish-Subscribe pattern for real-time messaging.
Publishers send messages, subscribers receive instantly.

Key Concepts:
  - PUBLISH: Send message to channel
  - SUBSCRIBE: Listen to channel
  - PSUBSCRIBE: Pattern subscribe
  - Real-time (no storage/history)
  - Fire-and-forget (messages not stored)
  - Multiple subscribers per channel

Common Operations:

1. PUBLISH - Send Message
   PUBLISH channel message

2. SUBSCRIBE - Listen to Channel
   SUBSCRIBE channel1 channel2

3. PSUBSCRIBE - Pattern Subscribe
   PSUBSCRIBE news.*

4. UNSUBSCRIBE - Stop Listening
   UNSUBSCRIBE channel

5. PUNSUBSCRIBE - Pattern Unsubscribe
   PUNSUBSCRIBE pattern

Characteristics:
  - No message history
  - Real-time delivery
  - One-to-many messaging
  - Fire-and-forget
  - Good for notifications

Use Cases:
  - Real-time notifications
  - Chat systems
  - Live updates
  - WebSocket events
  - Status updates
"""

import redis
import threading
import time

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

print(__doc__)

print("\n" + "="*70)
print("PUB/SUB - Real-Time Messaging")
print("="*70 + "\n")

# ============================================================
# 1. BASIC PUBLISH & SUBSCRIBE
# ============================================================
print("1. BASIC PUBLISH & SUBSCRIBE")
print("-" * 70)

def subscriber_thread():
    """Subscriber in separate thread"""
    sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = sub.pubsub()
    pubsub.subscribe("news:breaking")

    print("  [Subscriber] Waiting for messages...")

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"  [Subscriber] Received: {message['data']}")
            break

# Start subscriber in thread
thread = threading.Thread(target=subscriber_thread, daemon=True)
thread.start()

# Give subscriber time to start
time.sleep(0.5)

# Publish message
print("[Publisher] Sending message...")
r.publish("news:breaking", "Breaking news: Redis is awesome!")

# Wait for thread
thread.join(timeout=2)
print()

# ============================================================
# 2. MULTIPLE SUBSCRIBERS
# ============================================================
print("2. MULTIPLE SUBSCRIBERS - One-to-Many")
print("-" * 70)

message_received = []

def sub_worker(subscriber_id):
    """Worker that subscribes"""
    sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = sub.pubsub()
    pubsub.subscribe("broadcast:message")

    for message in pubsub.listen():
        if message['type'] == 'message':
            message_received.append((subscriber_id, message['data']))
            print(f"  [Subscriber {subscriber_id}] Got: {message['data']}")
            break

# Start 3 subscribers
threads = []
for i in range(1, 4):
    t = threading.Thread(target=sub_worker, args=(i,), daemon=True)
    t.start()
    threads.append(t)

time.sleep(0.5)

# Publish to all
print("[Publisher] Broadcasting to all subscribers...")
r.publish("broadcast:message", "Hello everyone!")

# Wait
for t in threads:
    t.join(timeout=2)

print(f"Messages received: {len(message_received)}\n")

# ============================================================
# 3. CHANNELS
# ============================================================
print("3. DIFFERENT CHANNELS")
print("-" * 70)

print("Channels available:")
print("  - notifications:user-1")
print("  - notifications:user-2")
print("  - alerts:system")
print("  - updates:live")

# Publish to different channels
for channel in ["notifications:user-1", "notifications:user-2", "alerts:system"]:
    count = r.publish(channel, f"Message to {channel}")
    print(f"  Published to {channel}: {count} subscribers")
print()

# ============================================================
# 4. PATTERN SUBSCRIBE
# ============================================================
print("4. PATTERN SUBSCRIBE - Wildcard Channels")
print("-" * 70)

print("Pattern: 'user:*' would match:")
print("  - user:123:login")
print("  - user:123:logout")
print("  - user:456:message")
print()

# ============================================================
# 5. REAL-WORLD: Notifications
# ============================================================
print("5. REAL-WORLD: Real-Time Notifications")
print("-" * 70)

def notification_listener(user_id):
    """Listen for user notifications"""
    sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = sub.pubsub()
    pubsub.subscribe(f"notifications:{user_id}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"  [{user_id}] Notification: {message['data']}")
            break

# Start listeners
user_id = "ujjawal-singh"
t = threading.Thread(target=notification_listener, args=(user_id,), daemon=True)
t.start()

time.sleep(0.3)

# Trigger notification
print(f"Sending notification to {user_id}...")
r.publish(f"notifications:{user_id}", "Someone liked your post!")

t.join(timeout=2)
print()

# ============================================================
# 6. REAL-WORLD: Live Updates
# ============================================================
print("6. REAL-WORLD: Live Chat Messages")
print("-" * 70)

def chat_listener(room_id):
    """Chat listener"""
    sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = sub.pubsub()
    pubsub.subscribe(f"chat:{room_id}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"  [Chat] {message['data']}")
            break

room = "room:dev-team"
t = threading.Thread(target=chat_listener, args=(room,), daemon=True)
t.start()

time.sleep(0.3)

print(f"Sending chat message...")
r.publish(f"chat:{room}", "ujjawal: Let's use Redis for caching!")

t.join(timeout=2)
print()

# ============================================================
# 7. REAL-WORLD: Live Dashboard Updates
# ============================================================
print("7. REAL-WORLD: Live Dashboard Updates")
print("-" * 70)

def dashboard_listener():
    """Dashboard listener"""
    sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = sub.pubsub()
    pubsub.subscribe("dashboard:updates")

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"  [Dashboard] Update: {message['data']}")
            break

t = threading.Thread(target=dashboard_listener, daemon=True)
t.start()

time.sleep(0.3)

print("Broadcasting dashboard update...")
r.publish("dashboard:updates", "New user signup: alice@example.com")

t.join(timeout=2)
print()

# ============================================================
# 8. PRACTICAL: Using Pub/Sub
# ============================================================
print("8. PRACTICAL: Event Publishing")
print("-" * 70)

print("Publishing events:")
print()

# Publish various events
events = [
    ("user:created", "New user: ujjawal@example.com"),
    ("order:placed", "Order #123 placed by ujjawal"),
    ("payment:received", "$99.99 received for order #123"),
]

for channel, message in events:
    count = r.publish(channel, message)
    print(f"  {channel}: {message}")
print()

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("PUB/SUB - KEY CONCEPTS")
print("="*70)
print("""
Publish:
  PUBLISH channel message      - Send message to channel
  Returns: number of subscribers

Subscribe:
  SUBSCRIBE channel1 channel2  - Listen to channels
  Blocking call - waits for messages

Pattern:
  PSUBSCRIBE pattern*          - Pattern matching
  PUNSUBSCRIBE pattern*        - Stop pattern

Use Cases:
  [OK] Real-time notifications
  [OK] Live chat
  [OK] Dashboard updates
  [OK] Event broadcasting
  [OK] Status updates
  [OK] System alerts
  [OK] Collaborative apps
  [OK] Live feeds

IMPORTANT - NO MESSAGE HISTORY:
  - Messages not stored
  - Subscribers must be connected
  - Missed messages are lost
  - Use Redis Streams for history!

Key Difference from Lists:
  - Lists: Queue (stored, consumed)
  - Pub/Sub: Broadcasting (not stored)

Typical Architecture:
  Events → PUBLISH → Channel → SUBSCRIBE → Clients

Benefits:
  [OK] Real-time delivery
  [OK] Decoupled systems
  [OK] Multiple subscribers
  [OK] Simple to implement

Limitations:
  [NO] No message history
  [NO] Subscribers must be online
  [NO] Not reliable for critical messages
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Build real-time notification system
2. Create live chat room
3. Implement dashboard updates
4. Build event bus for microservices
5. Create status update broadcaster
6. Implement real-time metrics viewer
7. Build collaborative editor (cursor updates)
8. Create order status tracker
9. Implement user presence system
10. Build real-time score updates

Challenge: Build complete notification system:
  - User gets notifications instantly
  - Multiple notification types
  - Unread count tracking
  - History in database (Pub/Sub for real-time)
  - Cleanup old notifications

Note: For persistent messages, use Redis Streams!

Modify the code and experiment!
""")


# ============================================================
# PRACTICE: Solutions for Pub/Sub
# ============================================================
print("="*70)
print("PRACTICE: Pub/Sub Exercises")
print("="*70 + "\n")

import json

def wait_for_message(channel, output_list, label):
  sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
  pubsub = sub.pubsub()
  pubsub.subscribe(channel)
  for message in pubsub.listen():
    if message['type'] == 'message':
      output_list.append((label, message['data']))
      print(f"  [{label}] {message['data']}")
      break

# 1. Build real-time notification system
print("1. Real-time notification system")
print("-" * 70)
notification_results = []
notification_user = "ujjawal-singh"
t = threading.Thread(target=wait_for_message, args=(f"notify:{notification_user}", notification_results, "Notify"), daemon=True)
t.start()
time.sleep(0.2)
r.publish(f"notify:{notification_user}", "New follower: alice")
t.join(timeout=2)
print()

# 2. Create live chat room
print("2. Live chat room")
print("-" * 70)
chat_results = []
t = threading.Thread(target=wait_for_message, args=("chat:room-1", chat_results, "Chat"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("chat:room-1", "ujjawal: Hello everyone!")
t.join(timeout=2)
print()

# 3. Implement dashboard updates
print("3. Dashboard updates")
print("-" * 70)
dashboard_results = []
t = threading.Thread(target=wait_for_message, args=("dashboard:updates", dashboard_results, "Dashboard"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("dashboard:updates", "New signup: user@example.com")
t.join(timeout=2)
print()

# 4. Build event bus for microservices
print("4. Event bus for microservices")
print("-" * 70)
event_results = []
t = threading.Thread(target=wait_for_message, args=("events:orders", event_results, "OrdersService"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("events:orders", json.dumps({"type": "order.created", "id": 123, "status": "new"}))
t.join(timeout=2)
print()

# 5. Create status update broadcaster
print("5. Status update broadcaster")
print("-" * 70)
status_results = []
t = threading.Thread(target=wait_for_message, args=("status:system", status_results, "Status"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("status:system", "All systems operational")
t.join(timeout=2)
print()

# 6. Implement real-time metrics viewer
print("6. Real-time metrics viewer")
print("-" * 70)
metrics_results = []
t = threading.Thread(target=wait_for_message, args=("metrics:live", metrics_results, "Metrics"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("metrics:live", json.dumps({"cpu": 67, "memory": 72, "requests_per_sec": 1450}))
t.join(timeout=2)
print()

# 7. Build collaborative editor (cursor updates)
print("7. Collaborative editor cursor updates")
print("-" * 70)
cursor_results = []
t = threading.Thread(target=wait_for_message, args=("editor:cursors", cursor_results, "Cursor"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("editor:cursors", json.dumps({"user": "alice", "line": 12, "column": 8}))
t.join(timeout=2)
print()

# 8. Create order status tracker
print("8. Order status tracker")
print("-" * 70)
order_results = []
t = threading.Thread(target=wait_for_message, args=("orders:status:123", order_results, "Orders"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("orders:status:123", "Order #123 shipped")
t.join(timeout=2)
print()

# 9. Implement user presence system
print("9. User presence system")
print("-" * 70)
presence_results = []
t = threading.Thread(target=wait_for_message, args=("presence:users", presence_results, "Presence"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("presence:users", "ujjawal-singh is online")
t.join(timeout=2)
print()

# 10. Build real-time score updates
print("10. Real-time score updates")
print("-" * 70)
score_results = []
t = threading.Thread(target=wait_for_message, args=("score:game-1", score_results, "Score"), daemon=True)
t.start()
time.sleep(0.2)
r.publish("score:game-1", json.dumps({"player": "ujjawal-singh", "score": 42}))
t.join(timeout=2)
print()

# Challenge: complete notification system
print("CHALLENGE: Complete notification system")
print("-" * 70)
notifications_channel = "notify:ujjawal-singh"
notifications_history_key = "history:notifications:ujjawal-singh"
notifications_unread_key = "unread:notifications:ujjawal-singh"
r.delete(notifications_history_key, notifications_unread_key)
r.set(notifications_unread_key, 0)

def send_notification(user_id, notification_type, message):
  payload = json.dumps({
    "user_id": user_id,
    "type": notification_type,
    "message": message,
    "ts": str(time.time())
  })
  r.publish(f"notify:{user_id}", payload)
  r.lpush(f"history:notifications:{user_id}", payload)
  r.ltrim(f"history:notifications:{user_id}", 0, 49)
  r.incr(f"unread:notifications:{user_id}")

def notification_listener_for_challenge():
  sub = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
  pubsub = sub.pubsub()
  pubsub.subscribe(notifications_channel)
  for message in pubsub.listen():
    if message['type'] == 'message':
      print(f"  [Instant] {message['data']}")
      break

listener = threading.Thread(target=notification_listener_for_challenge, daemon=True)
listener.start()
time.sleep(0.2)

send_notification("ujjawal-singh", "like", "Someone liked your post")
listener.join(timeout=2)
send_notification("ujjawal-singh", "comment", "New comment on your post")
send_notification("ujjawal-singh", "follow", "alice started following you")

print("  Unread count:", r.get(notifications_unread_key))
print("  History:")
for entry in r.lrange(notifications_history_key, 0, -1):
  print("   ", json.loads(entry))
print()

print("ALL PUB/SUB PRACTICE PROBLEMS COMPLETED")
print("="*70)
