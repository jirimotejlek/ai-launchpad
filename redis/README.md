# Redis Service

This directory contains the Redis cache service configuration for the AI Launchpad.

## Overview

Redis is an in-memory data structure store used for:
- Session management and caching
- Rate limiting and throttling
- Real-time data operations
- Message queues and pub/sub
- Distributed locking

## Components

- **README.md** - This file
- Uses official Redis 7 Alpine image (no custom Dockerfile needed)

## Enabling Redis

1. **Edit `services.config`** in the project root:
   ```bash
   ENABLE_REDIS=true
   ```

2. **Rebuild and start:**
   ```bash
   # Windows
   launchpad build-local
   launchpad run-local

   # macOS/Linux
   ./launchpad.sh build-local
   ./launchpad.sh run-local
   ```

## Connecting to Redis

### From within containers (e.g., client or llm-dispatcher):

**Connection Details:**
- Host: `redis`
- Port: `6379`
- Protocol: Redis protocol

**Example with redis-py:**
```python
import redis

# Connect to Redis
client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)

# Set a value
client.set('key', 'value')

# Get a value
value = client.get('key')
print(value)  # 'value'

# Set with expiration (30 seconds)
client.setex('session:123', 30, 'user_data')

# Increment counter
client.incr('page_views')
```

### From your host machine (for debugging):

The Redis port is exposed on `localhost:6379` during development. Use any Redis client:

```bash
# Using redis-cli
redis-cli -h localhost -p 6379

# Test connection
redis-cli -h localhost -p 6379 ping
# Should return: PONG
```

## Common Use Cases

### 1. Caching Database Queries

```python
import redis
import json

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def get_user(user_id):
    # Check cache first
    cache_key = f'user:{user_id}'
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Cache miss - fetch from database
    user = database.query_user(user_id)
    
    # Store in cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(user))
    return user
```

### 2. Rate Limiting

```python
import redis

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def check_rate_limit(user_id, limit=60):
    """Allow 60 requests per minute"""
    key = f'rate_limit:{user_id}:minute'
    
    # Increment counter
    current = redis_client.incr(key)
    
    # Set expiry on first request
    if current == 1:
        redis_client.expire(key, 60)
    
    return current <= limit
```

### 3. Session Management

```python
import redis
import json
from datetime import timedelta

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def create_session(session_id, user_data):
    """Create a session that expires in 1 hour"""
    key = f'session:{session_id}'
    redis_client.setex(
        key,
        timedelta(hours=1),
        json.dumps(user_data)
    )

def get_session(session_id):
    """Retrieve session data"""
    key = f'session:{session_id}'
    data = redis_client.get(key)
    return json.loads(data) if data else None

def delete_session(session_id):
    """Delete a session"""
    key = f'session:{session_id}'
    redis_client.delete(key)
```

### 4. Distributed Locking

```python
import redis
from redis.lock import Lock

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

def process_with_lock(resource_id):
    """Ensure only one process accesses the resource"""
    lock = redis_client.lock(
        f'lock:{resource_id}',
        timeout=10,  # Lock expires after 10 seconds
        blocking_timeout=5  # Wait up to 5 seconds to acquire
    )
    
    if lock.acquire(blocking=True):
        try:
            # Critical section - only one process at a time
            process_resource(resource_id)
        finally:
            lock.release()
```

### 5. Message Queue (Simple)

```python
import redis
import json

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Producer: Add to queue
def enqueue_task(queue_name, task_data):
    redis_client.lpush(queue_name, json.dumps(task_data))

# Consumer: Process queue
def process_queue(queue_name):
    while True:
        # Block until item available (0 = wait forever)
        item = redis_client.brpop(queue_name, timeout=0)
        if item:
            _, task_json = item
            task = json.loads(task_json)
            process_task(task)
```

### 6. Pub/Sub Pattern

```python
import redis

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Publisher
def publish_event(channel, message):
    redis_client.publish(channel, message)

# Subscriber
def subscribe_to_events(channel):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received: {message['data']}")
```

## Required Python Packages

Add to your service's `requirements.txt`:

```txt
redis==5.0.1
```

For async support:
```txt
redis[hiredis]==5.0.1
```

## Data Persistence

Redis data is stored in a Docker volume named `redis_data` using AOF (Append Only File) persistence. This ensures:
- Data persists across container restarts
- Write operations are logged for durability
- Automatic recovery on restart

**AOF vs RDB:**
- Current setup uses AOF for maximum durability
- Every write operation is logged
- Slight performance overhead but safer

**To backup data:**
```bash
docker run --rm -v ai-launchpad_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz /data
```

**To restore data:**
```bash
docker run --rm -v ai-launchpad_redis_data:/data -v $(pwd):/backup alpine tar xzf /backup/redis_backup.tar.gz -C /
```

## Troubleshooting

### Container won't start
Check logs:
```bash
launchpad logs redis
```

### Cannot connect from application
1. Verify Redis is running: `launchpad status`
2. Ensure your service is on the `backend` network
3. Use hostname `redis` not `localhost` from containers
4. Check Redis is responding: `redis-cli -h localhost -p 6379 ping`

### Connection refused
Make sure Redis container is healthy:
```bash
docker exec -it ai-launchpad_redis_1 redis-cli ping
```

### Memory issues
Redis will use up to 256MB by default (configured in docker-compose). If you need more:
```yaml
# In docker-compose.redis.yml
deploy:
  resources:
    limits:
      memory: 512M  # Increase as needed
```

### Clear all data
```bash
# Connect and flush
redis-cli -h localhost -p 6379 FLUSHALL

# Or reset volume
launchpad stop
docker volume rm ai-launchpad_redis_data
launchpad run-local
```

## Performance Tips

1. **Use connection pooling** - Reuse connections
   ```python
   pool = redis.ConnectionPool(host='redis', port=6379, max_connections=10)
   redis_client = redis.Redis(connection_pool=pool)
   ```

2. **Pipeline commands** - Reduce network round trips
   ```python
   pipe = redis_client.pipeline()
   pipe.set('key1', 'value1')
   pipe.set('key2', 'value2')
   pipe.execute()
   ```

3. **Use appropriate data structures**
   - Strings for simple key-value
   - Hashes for objects
   - Lists for queues
   - Sets for unique items
   - Sorted Sets for rankings

4. **Set expiration** - Prevent memory bloat
   ```python
   redis_client.setex('key', 3600, 'value')  # Expires in 1 hour
   ```

## Security Considerations

**Current setup:**
- No password by default (suitable for development)
- Only accessible within Docker network
- Port 6379 exposed for development only

**For production:**
1. **Set a password:**
   - Create `.env.redis` file:
     ```bash
     REDIS_PASSWORD=your-secure-password
     ```
   - Update `docker-compose.redis.yml`:
     ```yaml
     env_file:
       - .env.redis
     ```
   - Connect with password:
     ```python
     redis.Redis(host='redis', port=6379, password='your-secure-password')
     ```

2. **Remove port exposure** - Comment out ports in docker-compose.redis.yml
3. **Enable TLS** - For external connections
4. **Rename dangerous commands** - FLUSHALL, FLUSHDB, CONFIG

## Resource Usage

- **Memory**: ~128-256MB (configurable)
- **CPU**: ~0.1-0.25 cores
- **Disk**: Base image ~30MB + data (AOF file)
- **Network**: Connected to `backend` network

## Monitoring

### Check memory usage:
```bash
redis-cli -h localhost -p 6379 INFO memory
```

### Check connected clients:
```bash
redis-cli -h localhost -p 6379 CLIENT LIST
```

### Monitor commands in real-time:
```bash
redis-cli -h localhost -p 6379 MONITOR
```

### Get statistics:
```bash
redis-cli -h localhost -p 6379 INFO stats
```

## Advanced Configuration

You can customize Redis behavior by modifying the command in `docker-compose.redis.yml`:

```yaml
command: >
  redis-server
  --appendonly yes
  --maxmemory 256mb
  --maxmemory-policy allkeys-lru
  --save 900 1
  --save 300 10
```

**Common options:**
- `--maxmemory` - Maximum memory limit
- `--maxmemory-policy` - Eviction policy (allkeys-lru, volatile-ttl, etc.)
- `--appendonly` - Enable AOF persistence
- `--save` - RDB snapshot intervals
- `--requirepass` - Set password

See [Redis documentation](https://redis.io/docs/management/config/) for all available options.

## Redis CLI Quick Reference

```bash
# Connect
redis-cli -h localhost -p 6379

# Basic commands
SET key value
GET key
DEL key
EXISTS key
KEYS pattern
TTL key
EXPIRE key seconds

# Counters
INCR counter
DECR counter
INCRBY counter 10

# Lists
LPUSH list value
RPUSH list value
LPOP list
RPOP list
LRANGE list 0 -1

# Hashes
HSET hash field value
HGET hash field
HGETALL hash
HDEL hash field

# Sets
SADD set member
SMEMBERS set
SISMEMBER set member
SREM set member

# Sorted Sets
ZADD zset score member
ZRANGE zset 0 -1
ZRANK zset member

# Info
INFO
DBSIZE
CLIENT LIST
MONITOR
```

## Use Cases in AI Launchpad

Redis is particularly useful for:

1. **API Gateway** - Rate limiting, API key caching, request throttling
2. **Session Management** - User sessions, authentication tokens
3. **Billing Service** - Token balance caching, transaction queuing
4. **Analytics** - Real-time counters, usage tracking
5. **Background Jobs** - Task queues, job status tracking
6. **Caching** - Database query results, expensive computations

## Further Reading

- [Redis Documentation](https://redis.io/docs/)
- [Redis Commands](https://redis.io/commands/)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
- [redis-py Documentation](https://redis-py.readthedocs.io/)


