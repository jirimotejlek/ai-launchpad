FROM postgres:16-alpine

# Set default environment variables (can be overridden by docker-compose)
ENV POSTGRES_DB=ai_launchpad
ENV POSTGRES_USER=admin

# Copy initialization script
COPY init.sql /docker-entrypoint-initdb.d/

# The official postgres image automatically runs scripts in /docker-entrypoint-initdb.d/
# on container startup if the database doesn't exist yet

EXPOSE 5432

