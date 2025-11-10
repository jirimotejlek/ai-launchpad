# PostgreSQL Service

This directory contains the PostgreSQL database service configuration for the AI Launchpad.

## Overview

PostgreSQL is used for persistent data storage, including:
- User authentication (username, email, password)
- User preferences and settings
- Application data

## Components

- **Dockerfile** - PostgreSQL 16 Alpine-based image (minimal footprint ~16MB)
- **init.sql** - Database initialization script with schema
- **README.md** - This file

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `idx_users_username` - Fast username lookups
- `idx_users_email` - Fast email lookups

**Triggers:**
- `update_users_updated_at` - Automatically updates `updated_at` on row changes

## Enabling PostgreSQL

1. **Edit `services.config`** in the project root:
   ```bash
   ENABLE_POSTGRES=true
   ```

2. **Create `.env.postgres` file** with database credentials:
   ```bash
   cp env_templates/postgres.env .env.postgres
   # Edit .env.postgres and set a secure password
   ```

3. **Start the service**:
   ```bash
   # Windows
   launchpad build-local
   launchpad run-local

   # macOS/Linux
   ./launchpad.sh build-local
   ./launchpad.sh run-local
   ```

## Connecting to PostgreSQL

### From within containers (e.g., client or llm-dispatcher):

**Connection Details:**
- Host: `postgres`
- Port: `5432`
- Database: `ai_launchpad` (or as configured in .env.postgres)
- User: As configured in `.env.postgres`
- Password: As configured in `.env.postgres`

**Example with SQLAlchemy:**
```python
from flask_sqlalchemy import SQLAlchemy
import os

# Connection string using environment variables
db_user = os.getenv('DB_USER', 'admin')
db_name = os.getenv('DB_NAME', 'ai_launchpad')
db_password = os.getenv('POSTGRES_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@postgres:5432/{db_name}'
db = SQLAlchemy(app)
```

**Example with psycopg2:**
```python
import psycopg2
import os

conn = psycopg2.connect(
    host="postgres",
    port=5432,
    database=os.getenv('DB_NAME', 'ai_launchpad'),
    user=os.getenv('DB_USER', 'admin'),
    password=os.getenv('POSTGRES_PASSWORD')
)
```

### From your host machine (for debugging):

The PostgreSQL port is exposed on `localhost:5432` during development. Use any PostgreSQL client:

```bash
# Using psql command line
psql -h localhost -p 5432 -U admin -d ai_launchpad

# Or use GUI tools like pgAdmin, DBeaver, etc.
```

## Required Python Packages

Add to your service's `requirements.txt`:

```txt
# For SQLAlchemy (recommended)
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9

# Or for direct connection
psycopg2-binary==2.9.9
```

## Security Best Practices

1. **Never commit `.env.postgres` file** - It's already in `.gitignore`
2. **Keep database credentials separate** - `.env.postgres` is separate from your main `.env` for LLM config
3. **Use strong passwords** - At least 16 characters, mixed case, numbers, symbols
3. **Hash passwords** - Never store plain text passwords:
   ```python
   from werkzeug.security import generate_password_hash, check_password_hash
   
   # When creating user
   password_hash = generate_password_hash(password)
   
   # When authenticating
   is_valid = check_password_hash(stored_hash, provided_password)
   ```
4. **Use environment variables** - Never hardcode credentials
5. **Remove port exposure in production** - Comment out ports in docker-compose.postgres.yml

## Data Persistence

Database data is stored in a Docker volume named `postgres_data`. This ensures:
- Data persists across container restarts
- Data survives container removal
- Easy backups via volume management

**To backup data:**
```bash
docker run --rm -v ai-launchpad_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

**To restore data:**
```bash
docker run --rm -v ai-launchpad_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## Troubleshooting

### Container won't start
Check logs:
```bash
launchpad logs postgres
```

### Cannot connect from application
1. Verify PostgreSQL is running: `launchpad status`
2. Check credentials in `.env.postgres` match your application
3. Ensure your service is on the `backend` network
4. Use hostname `postgres` not `localhost` from containers

### Reset database
```bash
launchpad stop
docker volume rm ai-launchpad_postgres_data
launchpad run-local
```

## Resource Usage

- **Memory**: ~256-512MB
- **CPU**: ~0.5 cores
- **Disk**: Base image 16MB + data
- **Network**: Connected to `backend` network

## Advanced Configuration

You can customize PostgreSQL settings by modifying the `docker-compose.postgres.yml` file's command section:

```yaml
command: >
  postgres
  -c shared_buffers=128MB
  -c max_connections=50
  -c effective_cache_size=256MB
```

See [PostgreSQL documentation](https://www.postgresql.org/docs/current/runtime-config.html) for all available options.

