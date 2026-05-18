"""
COURSE 3: LISTS - Queues, Feeds, and Sequences
===============================================

THEORY:
Lists in Redis are ordered collections (like arrays/queues).

Key Concepts:
  - Ordered: position matters
  - Duplicates allowed
  - Can grow very large (millions of items)
  - Fast for adding/removing at ends
  - Slow for accessing middle

Common Operations:

1. LPUSH / RPUSH - Add to List
   LPUSH key val        - Add to LEFT (front)
   RPUSH key val        - Add to RIGHT (back)

2. LPOP / RPOP - Remove from List
   LPOP key             - Remove from LEFT
   RPOP key             - Remove from RIGHT

3. LLEN - List Length
   LLEN key             - How many items

4. LRANGE - Get Range
   LRANGE key 0 -1      - Get all items
   LRANGE key 0 9       - Get first 10

5. LINDEX - Get by Position
   LINDEX key 0         - Get first item
   LINDEX key -1        - Get last item

6. LSET - Set Value at Position
   LSET key 0 value     - Set first item

7. LTRIM - Keep Range, Delete Rest
   LTRIM key 0 99       - Keep first 100, delete rest

8. LINSERT - Insert Before/After
   LINSERT key BEFORE pivot value

9. RPOPLPUSH - Move Between Lists
   RPOPLPUSH source dest - Pop from source, push to dest

Performance:
  - LPUSH/RPUSH/LPOP/RPOP: O(1) - VERY FAST
  - LRANGE: O(N) where N = number of items
  - LINDEX: O(N) - linear time

Use Cases:
  - Task queues (process jobs)
  - Activity feeds (recent posts, messages)
  - Notifications
  - Message buffers
  - Undo/redo stacks
  - Sliding window

Never Use For:
  - Random access patterns (use sets or hashes)
  - Very large lists with frequent middle access
"""

import redis
import json
from datetime import datetime

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
r.flushdb()

print(__doc__)

print("\n" + "="*70)
print("LISTS - PRACTICAL EXAMPLES")
print("="*70 + "\n")

user = "ujjawal-singh"

# ============================================================
# 1. BASIC LPUSH & RPUSH
# ============================================================
print("1. LPUSH (add to front) vs RPUSH (add to back)")
print("-" * 70)

# Start with empty list
r.delete(f"{user}:notifications")

# Add notifications (most recent to left)
r.lpush(f"{user}:notifications", "Old notification")
r.lpush(f"{user}:notifications", "Medium notification")
r.lpush(f"{user}:notifications", "New notification")

# View list
notifications = r.lrange(f"{user}:notifications", 0, -1)
print(f"Notifications: {notifications}")
print("  -> Most recent is first!\n")

# ============================================================
# 2. TASK QUEUE - Producer/Consumer
# ============================================================
print("2. TASK QUEUE - Processing Jobs")
print("-" * 70)

queue = f"{user}:tasks"
r.delete(queue)

# Producer: Add tasks
tasks = [
    {'id': 1, 'type': 'send_email', 'to': 'friend@example.com'},
    {'id': 2, 'type': 'generate_report', 'format': 'pdf'},
    {'id': 3, 'type': 'backup_database', 'size': '10GB'},
    {'id': 4, 'type': 'send_notification', 'user': 'all'},
]

print("Producer: Adding tasks to queue...")
for task in tasks:
    r.rpush(queue, json.dumps(task))
    print(f"  Added task: {task['type']}")

print(f"\nQueue length: {r.llen(queue)} tasks\n")

# Consumer: Process tasks
print("Consumer: Processing tasks...")
while True:
    # LPOP removes and returns first item
    task_json = r.lpop(queue)
    if not task_json:
        break

    task = json.loads(task_json)
    print(f"  Processing: {task['type']} (Task #{task['id']})")

print(f"Queue length after processing: {r.llen(queue)}\n")

# ============================================================
# 3. ACTIVITY FEED
# ============================================================
print("3. ACTIVITY FEED - Recent Posts")
print("-" * 70)

feed = f"{user}:feed"
r.delete(feed)

# Simulate posts appearing
posts = [
    {'author': 'alice', 'content': 'Just learned Python!', 'likes': 5},
    {'author': 'bob', 'content': 'Building with React', 'likes': 12},
    {'author': 'charlie', 'content': 'Docker is awesome', 'likes': 8},
    {'author': 'ujjawal', 'content': 'Redis mastery!', 'likes': 100},
    {'author': 'diana', 'content': 'ML algorithms', 'likes': 25},
]

print("Posts being added to feed...")
for post in posts:
    r.lpush(feed, json.dumps(post))

# Show first 3 posts
print("\nLatest 3 posts in feed:")
recent_posts = r.lrange(feed, 0, 2)
for i, post_json in enumerate(recent_posts):
    post = json.loads(post_json)
    print(f"  {i+1}. {post['author']}: {post['content']} ({post['likes']} likes)")

print(f"\nTotal posts in feed: {r.llen(feed)}\n")

# ============================================================
# 4. LINDEX & LSET - Access & Modify
# ============================================================
print("4. LINDEX & LSET - Access & Modify Items")
print("-" * 70)

# Get first (most recent) post
first_post_json = r.lindex(feed, 0)
first_post = json.loads(first_post_json)
print(f"Most recent post: {first_post['author']} - {first_post['content']}")

# Get last post
last_post_json = r.lindex(feed, -1)
last_post = json.loads(last_post_json)
print(f"Oldest post: {last_post['author']} - {last_post['content']}\n")

# Update a post (increase likes)
print("Updating likes for second post...")
second_post_json = r.lindex(feed, 1)
second_post = json.loads(second_post_json)
second_post['likes'] += 50
r.lset(feed, 1, json.dumps(second_post))
print(f"New likes: {second_post['likes']}\n")

# ============================================================
# 5. LTRIM - Keep Recent, Discard Old
# ============================================================
print("5. LTRIM - Keep Recent 100, Delete Older")
print("-" * 70)

# Simulate timeline with many posts
timeline = f"{user}:timeline"
r.delete(timeline)

print("Adding 250 posts...")
for i in range(250):
    post = {'id': i, 'content': f'Post #{i}'}
    r.rpush(timeline, json.dumps(post))

print(f"Posts before trim: {r.llen(timeline)}")

# Keep only first 100, delete rest
r.ltrim(timeline, 0, 99)
print(f"Posts after trim: {r.llen(timeline)} (kept only newest 100)\n")

# ============================================================
# 6. RPOPLPUSH - Move Between Queues
# ============================================================
print("6. RPOPLPUSH - Archive Processed Tasks")
print("-" * 70)

# Active queue
active = f"{user}:active-tasks"
r.delete(active)

# Archive queue
archive = f"{user}:archived-tasks"
r.delete(archive)

# Add some tasks
for i in range(5):
    r.rpush(active, json.dumps({'id': i, 'status': 'pending'}))

print(f"Active tasks: {r.llen(active)}")
print(f"Archived tasks: {r.llen(archive)}\n")

# Process tasks
print("Moving tasks from active to archive...")
for _ in range(3):
    # Move from one list to another atomically
    r.rpoplpush(active, archive)

print(f"Active tasks now: {r.llen(active)}")
print(f"Archived tasks now: {r.llen(archive)}\n")

# ============================================================
# 7. LINSERT - Insert at Specific Position
# ============================================================
print("7. LINSERT - Insert Before/After")
print("-" * 70)

priorities = f"{user}:priorities"
r.delete(priorities)

r.rpush(priorities, "Task A", "Task C")
print(f"Initial: {r.lrange(priorities, 0, -1)}")

# Insert before Task C
r.linsert(priorities, "BEFORE", "Task C", "Task B")
print(f"After insert: {r.lrange(priorities, 0, -1)}\n")

# ============================================================
# 8. REAL-WORLD: Redis Queue Manager
# ============================================================
print("8. REAL-WORLD: Multi-Priority Queue")
print("-" * 70)

class TaskQueue:
    def __init__(self, redis_conn, user):
        self.r = redis_conn
        self.user = user
        self.high_priority = f"{user}:queue:high"
        self.normal_priority = f"{user}:queue:normal"
        self.low_priority = f"{user}:queue:low"

    def add_task(self, task, priority="normal"):
        queue = {
            "high": self.high_priority,
            "normal": self.normal_priority,
            "low": self.low_priority
        }[priority]
        self.r.rpush(queue, json.dumps(task))

    def get_next_task(self):
        # Process high priority first
        for queue in [self.high_priority, self.normal_priority, self.low_priority]:
            task_json = self.r.lpop(queue)
            if task_json:
                return json.loads(task_json)
        return None

    def queue_lengths(self):
        return {
            'high': self.r.llen(self.high_priority),
            'normal': self.r.llen(self.normal_priority),
            'low': self.r.llen(self.low_priority)
        }

# Use the queue manager
queue_mgr = TaskQueue(r, user)

# Add tasks with different priorities
r.delete(f"{user}:queue:high")
r.delete(f"{user}:queue:normal")
r.delete(f"{user}:queue:low")

queue_mgr.add_task({'id': 1, 'type': 'urgent_fix'}, priority='high')
queue_mgr.add_task({'id': 2, 'type': 'feature'}, priority='normal')
queue_mgr.add_task({'id': 3, 'type': 'documentation'}, priority='low')
queue_mgr.add_task({'id': 4, 'type': 'critical_bug'}, priority='high')
queue_mgr.add_task({'id': 5, 'type': 'refactor'}, priority='normal')

print("Queue status:")
lengths = queue_mgr.queue_lengths()
for priority, count in lengths.items():
    print(f"  {priority}: {count} tasks")

print("\nProcessing tasks in priority order:")
for i in range(5):
    task = queue_mgr.get_next_task()
    if task:
        print(f"  Processing: {task['type']} (Priority based)")

print()

# ============================================================
# 9. REAL-WORLD: Notification Bell (Last 10 Notifications)
# ============================================================
print("9. REAL-WORLD: Notification System")
print("-" * 70)

notifications_key = f"{user}:notifications"
r.delete(notifications_key)

def notify(message):
    """Add notification and keep only last 10"""
    notification = {
        'timestamp': str(datetime.now()),
        'message': message
    }
    r.lpush(notifications_key, json.dumps(notification))
    # Keep only last 10
    r.ltrim(notifications_key, 0, 9)

# Simulate notifications
messages = [
    "Someone liked your post",
    "New follower: Alice",
    "Comment on your post: 'Great work!'",
    "Your post reached 100 likes",
    "Alice followed you back",
]

print("Sending notifications...")
for msg in messages:
    notify(msg)
    print(f"  [!] {msg}")

print(f"\nYour notification bell shows:")
notifs = r.lrange(notifications_key, 0, -1)
for i, notif_json in enumerate(notifs, 1):
    notif = json.loads(notif_json)
    print(f"  {i}. {notif['message']}")

print()

# ============================================================
# SUMMARY
# ============================================================
print("="*70)
print("LISTS - KEY COMMANDS SUMMARY")
print("="*70)
print("""
Add:
  LPUSH key value             - Add to left (front)
  RPUSH key value             - Add to right (back)

Remove:
  LPOP key                    - Remove from left
  RPOP key                    - Remove from right

Access:
  LLEN key                    - Get length
  LINDEX key position         - Get item at position
  LRANGE key start stop       - Get range

Modify:
  LSET key index value        - Set value at position
  LTRIM key start stop        - Keep range, delete rest
  LINSERT key BEFORE pivot val - Insert

Move:
  RPOPLPUSH source dest       - Move between lists

Use Cases:
  [OK] Task queues
  [OK] Job processing (FIFO)
  [OK] Activity feeds
  [OK] Notifications
  [OK] Undo/redo stacks
  [OK] Message buffers
  [OK] Rate limiting (sliding window)

Complexity:
  [FAST] LPUSH, RPUSH, LPOP, RPOP = O(1)
  [SLOW] LINDEX, LRANGE = O(N)
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Create a task queue with 100 tasks, process them all
2. Build an activity feed that keeps only the last 50 posts
3. Implement a notification system that shows last 5 messages
4. Create a message queue with different priorities
5. Build a rate limiter using LPUSH + LTRIM (sliding window)
6. Implement an undo/redo stack (2 lists, back and forth)
7. Create a leaderboard using lists (sorted by score)

Challenge: Build a complete chat system:
  - Messages are lists
  - Users can only see last 100 messages
  - New messages added to front
  - Delete oldest after 100

Modify the code and experiment!
""")


# ============================================================
# PRACTICE: Solutions
# ============================================================
print("="*70)
print("PRACTICE: Lists Exercises")
print("="*70 + "\n")

# Task 1: Create a task queue with 100 tasks, process them all
print("1. Task queue with 100 tasks - produce and consume")
print("-" * 70)
big_queue = f"{user}:big-tasks"
r.delete(big_queue)

for i in range(1, 101):
  r.rpush(big_queue, json.dumps({'id': i, 'job': f'job_{i}'}))

print(f"  Produced {r.llen(big_queue)} tasks")
processed = 0
while True:
  job = r.lpop(big_queue)
  if not job:
    break
  processed += 1

print(f"  Processed {processed} tasks, remaining: {r.llen(big_queue)}\n")

# Task 2: Activity feed that keeps only last 50 posts
print("2. Activity feed - keep only last 50 posts")
print("-" * 70)
feed_key = f"{user}:activity:50"
r.delete(feed_key)

for i in range(60):
  post = {'id': i, 'content': f'Post #{i}'}
  r.lpush(feed_key, json.dumps(post))
  # keep only last 50 posts
  r.ltrim(feed_key, 0, 49)

print(f"  Posts kept: {r.llen(feed_key)} (should be 50)")
first = json.loads(r.lindex(feed_key, 0))
last = json.loads(r.lindex(feed_key, -1))
print(f"  Newest post id: {first['id']}, Oldest kept id: {last['id']}\n")

# Task 3: Notification system that shows last 5 messages
print("3. Notification system - last 5 messages")
print("-" * 70)
notif_key = f"{user}:notifs:5"
r.delete(notif_key)

def send_notification(msg):
  r.lpush(notif_key, json.dumps({'time': str(datetime.now()), 'msg': msg}))
  r.ltrim(notif_key, 0, 4)

msgs = [
  'Welcome!', 'You have a new follower', 'Someone liked your post',
  'New comment on your post', 'Your repo got a star', 'Reminder: Meeting at 3PM'
]
for m in msgs:
  send_notification(m)

print(f"  Notifications stored (most recent first): {r.llen(notif_key)}")
for i, n in enumerate(r.lrange(notif_key, 0, -1), 1):
  print(f"   {i}.", json.loads(n)['msg'])
print()

# Task 4: Message queue with different priorities
print("4. Message queue with priorities")
print("-" * 70)
high = f"{user}:msg:high"
normal = f"{user}:msg:normal"
low = f"{user}:msg:low"
for k in (high, normal, low):
  r.delete(k)

def add_msg(task, priority='normal'):
  key = {'high': high, 'normal': normal, 'low': low}[priority]
  r.rpush(key, json.dumps({'task': task, 'priority': priority}))

add_msg('urgent_fix', 'high')
add_msg('feature_work', 'normal')
add_msg('minor_cleanup', 'low')
add_msg('security_patch', 'high')

print("  Queue lengths:")
print("   high:", r.llen(high), " normal:", r.llen(normal), " low:", r.llen(low))

print("  Processing in priority order:")
for _ in range(r.llen(high) + r.llen(normal) + r.llen(low)):
  job = None
  for q in (high, normal, low):
    j = r.lpop(q)
    if j:
      job = json.loads(j)
      print("   Processing:", job['task'], "(priority=", job['priority'], ")")
      break
  if not job:
    break
print()

# Task 5: Rate limiter using LPUSH + LTRIM (sliding window)
print("5. Rate limiter (sliding window) - allow 5 requests per 60s")
print("-" * 70)
rl_key = f"rate:{user}:sliding"
r.delete(rl_key)

import time as _t

def allow_request_sliding(user_id, limit=5, window=60):
  key = f"rate:{user_id}:sliding"
  now = int(_t.time())
  # Push current timestamp at head
  r.lpush(key, now)
  # Remove timestamps older than window (we'll trim by count and then check oldest)
  r.ltrim(key, 0, limit - 1)
  count = r.llen(key)
  if count < limit:
    return True, count
  # When count == limit, check oldest timestamp
  oldest = int(r.lindex(key, -1))
  if now - oldest < window:
    return False, count
  return True, count

print("  Simulating 8 rapid requests:")
for i in range(8):
  ok, c = allow_request_sliding(user, limit=5, window=60)
  print(f"   Request {i+1}:", "ALLOWED" if ok else "BLOCKED", f"({c}/5)")
  _t.sleep(0.2)
print()

# Task 6: Undo/Redo stack (2 lists)
print("6. Undo/Redo stack simulation")
print("-" * 70)
undo = f"{user}:undo"
redo = f"{user}:redo"
for k in (undo, redo):
  r.delete(k)

def do_action(action):
  # push to undo and clear redo
  r.lpush(undo, action)
  r.delete(redo)

def undo_action():
  a = r.lpop(undo)
  if a:
    r.lpush(redo, a)
    return a
  return None

def redo_action():
  a = r.lpop(redo)
  if a:
    r.lpush(undo, a)
    return a
  return None

do_action('type:Hello')
do_action('type:World')
do_action('delete:5')

print("  Undoing two actions:")
print("   undone:", undo_action())
print("   undone:", undo_action())
print("  Redoing one action:")
print("   redone:", redo_action())
print()

# Task 7: Leaderboard using lists (sorted by score via Python)
print("7. Leaderboard using lists (sorted client-side)")
print("-" * 70)
lb_key = f"{user}:leaderboard:list"
r.delete(lb_key)

players = [
  ('alice', 150), ('bob', 200), ('charlie', 180), ('diana', 220), ('ed', 175)
]
for name, score in players:
  # store as JSON to preserve structure
  r.rpush(lb_key, json.dumps({'user': name, 'score': score}))

all_players = [json.loads(x) for x in r.lrange(lb_key, 0, -1)]
sorted_players = sorted(all_players, key=lambda p: p['score'], reverse=True)

print("  Top players:")
for i, p in enumerate(sorted_players, 1):
  print(f"   {i}. {p['user']} - {p['score']}")
print()

# Challenge: Chat system - keep last 100 messages per room
print("CHALLENGE: Simple chat system (last 100 messages)")
print("-" * 70)
def send_message(room, sender, text):
  key = f"chat:{room}:messages"
  msg = json.dumps({'time': str(datetime.now()), 'from': sender, 'text': text})
  r.lpush(key, msg)
  r.ltrim(key, 0, 99)  # keep last 100 messages

chat_room = 'general'
chat_key = f"chat:{chat_room}:messages"
r.delete(chat_key)

for i in range(105):
  send_message(chat_room, f'user{i%5}', f'Message number {i}')

print(f"  Messages stored: {r.llen(chat_key)} (should be 100)")
print("  Most recent message:", json.loads(r.lindex(chat_key, 0))['text'])
print("  Oldest kept message:", json.loads(r.lindex(chat_key, -1))['text'])

print("\nALL LIST PRACTICE PROBLEMS COMPLETED")
print("="*70)
