# PostgreSQL Migration Guide

This guide describes the migration from SQLite to PostgreSQL for the Community Backend Service.

## Migration Steps Completed

1. Installed PostgreSQL adapter (psycopg2-binary)
2. Updated database connection configuration to use PostgreSQL
3. Updated Alembic configuration to use PostgreSQL
4. Migrated existing data from SQLite to PostgreSQL
5. Updated Docker configuration to include PostgreSQL
6. Added development environment setup with hot reloading

## Local Development Setup

### Prerequisites

1. Install PostgreSQL on your system
2. Install the Python PostgreSQL adapter:
   ```bash
   pip install psycopg2-binary
   ```
