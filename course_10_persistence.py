"""
COURSE 10: PERSISTENCE - RDB & AOF
===================================

THEORY:
Persistence saves Redis data to disk for recovery.
Two strategies: RDB (snapshots) and AOF (log).

RDB (Redis Database):
  - Snapshot at intervals
  - Binary format (compact)
  - Fast loading
  - Loss since last snapshot
  - save 900 1 = snapshot every 15 min if 1+ change

AOF (Append Only File):
  - Record every write operation
  - Text format (readable)
  - More durable
  - Larger file size
  - appendonly yes = enable AOF

When to Use:
  - RDB: Fast recovery, good performance
  - AOF: Data safety critical
  - Both: Best of both (dual persistence)
  - None: Cache (can lose data)
"""

import redis
import time
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

print(__doc__)

print("\n" + "="*70)
print("PERSISTENCE - RDB & AOF")
print("="*70 + "\n")

# ============================================================
# 1. CHECK PERSISTENCE CONFIG
# ============================================================
print("1. CHECK PERSISTENCE CONFIGURATION")
print("-" * 70)

# Get config
config = r.config_get("save")
appendonly = r.config_get("appendonly")

print(f"RDB save policy: {config['save']}")
print(f"AOF enabled: {appendonly['appendonly']}\n")

# ============================================================
# 2. CREATE DATA
# ============================================================
print("2. CREATE DATA TO PERSIST")
print("-" * 70)

r.set("user:ujjawal:name", "Ujjawal Singh")
r.set("user:ujjawal:email", "ujjawal@example.com")
r.lpush("notifications:ujjawal", "notification1", "notification2")
r.hset("settings:ujjawal", mapping={"theme": "dark", "language": "en"})

print("Data created:")
print(f"  Keys: {r.keys('*')}\n")

# ============================================================
# 3. SAVE SNAPSHOT
# ============================================================
print("3. MANUAL SAVE - Create RDB Snapshot")
print("-" * 70)

print("Executing BGSAVE (background save)...")
r.bgsave()
print("Snapshot in progress (async)")
print(f"  Saved data size can be checked with: INFO stats\n")

# ============================================================
# 4. SIMULATING BACKUP
# ============================================================
print("4. BACKUP STRATEGY")
print("-" * 70)

print("In production, backup dump.rdb regularly:")
print("  1. Run: redis-cli BGSAVE")
print("  2. Copy: /var/lib/redis/dump.rdb to backup location")
print("  3. Schedule: Cron job daily")
print("  4. Store: Multiple locations (S3, cloud storage)\n")

# ============================================================
# 5. RESTORE PROCESS
# ============================================================
print("5. RESTORE PROCESS")
print("-" * 70)

print("To restore from backup:")
print("  1. Stop Redis: redis-cli SHUTDOWN")
print("  2. Copy dump.rdb: restore-backup to /var/lib/redis/")
print("  3. Start Redis: redis-server")
print("  4. Data is automatically loaded\n")

# ============================================================
# 6. PERSISTENCE INFO
# ============================================================
print("6. CHECK PERSISTENCE INFO")
print("-" * 70)

# Get replication info
repl_info = r.info('replication')
print("Replication status:")
print(f"  Role: {repl_info.get('role', 'unknown')}\n")

# ============================================================
# 7. REAL-WORLD: Backup Plan
# ============================================================
print("7. REAL-WORLD: Backup & Disaster Recovery")
print("-" * 70)

print("Recommended Configuration:")
print("""
  # redis.conf

  # RDB - Snapshot every 15 min if changed
  save 900 1

  # AOF - Write log for durability
  appendonly yes
  appendfsync everysec  # Sync every second

  # Replication - For HA
  replicaof master 6379

  # Backup script (cron job)
  0 2 * * * /backup/backup-redis.sh
""")
print()

# ============================================================
# 8. AOF (Append Only File)
# ============================================================
print("8. AOF - Command Log")
print("-" * 70)

print("With AOF enabled (appendonly yes):")
print("  - Every write command logged to appendonly.aof")
print("  - Textfile with all commands executed")
print("  - Slower than RDB but safer")
print("  - Can be replayed after crash")
print("  - BGREWRITEAOF compresses it\n")

# ============================================================
# 9. OPERATIONAL PERSISTENCE
# ============================================================
print("9. OPERATIONAL GUIDELINES")
print("-" * 70)

print("DO:")
print("  [OK] Enable persistence on production")
print("  [OK] Use both RDB + AOF for safety")
print("  [OK] Regular backups")
print("  [OK] Test recovery procedures")
print("  [OK] Monitor disk space")

print("\nDON'T:")
print("  [NO] Disable persistence on critical data")
print("  [NO] Backup to same disk")
print("  [NO] Assume memory is sufficient")
print("  [NO] Skip testing backups\n")

# ============================================================
# 10. SUMMARY
# ============================================================
print("="*70)
print("PERSISTENCE - CONFIGURATION SUMMARY")
print("="*70)
print("""
RDB (Redis Database) - Snapshots:
  save 900 1                   - Snapshot every 900s if 1+ change
  save 300 10                  - Snapshot every 300s if 10+ changes
  bgsave                       - Manual snapshot
  bgsave command               - Execute in background

AOF (Append Only File) - Command Log:
  appendonly yes               - Enable AOF
  appendfsync always           - Sync immediately (slow)
  appendfsync everysec         - Sync every second
  appendfsync no               - Let OS decide (fast)
  bgrewriteaof                 - Compress AOF file

Backup:
  lastsave                     - Get timestamp of last RDB save
  CONFIG GET save              - Get RDB policy
  SHUTDOWN                     - Safe shutdown (flush before save)

Comparison:
  RDB:
    [+] Compact, fast loading
    [-] Loss since last snapshot

  AOF:
    [+] Every write saved, safer
    [-] Larger, slower

  Both (recommended):
    [+] Safety + Performance
    [-] More disk usage

Restore:
  1. Stop Redis
  2. Copy backup to /var/lib/redis/dump.rdb (RDB)
  3. Start Redis - auto loads

Test Recovery:
  1. Never trust backups you haven't tested
  2. Regular restore tests in staging
  3. Verify all data is restored
  4. Check replication works
""")

# ============================================================
# PRACTICE PROBLEMS
# ============================================================
print("="*70)
print("PRACTICE: Try These!")
print("="*70)
print("""
1. Configure RDB snapshots
2. Enable and test AOF
3. Create backup script
4. Simulate data loss and recovery
5. Test replication setup
6. Monitor persistence performance
7. Implement backup retention
8. Setup automated backups
9. Test disaster recovery
10. Create monitoring alerts

Production Deployment Checklist:
  [ ] Enable persistence (RDB + AOF)
  [ ] Configure save intervals
  [ ] Setup backup script
  [ ] Test recovery procedure
  [ ] Monitor disk usage
  [ ] Setup replication
  [ ] Configure Sentinel
  [ ] Document recovery steps
  [ ] Test failover
  [ ] Setup monitoring/alerts
""")

print("\nNote: This is a reference course. Actual RDB/AOF")
print("configuration is in docker-compose.yml and redis.conf")
