-- Database initialization script for TaskManager
-- This script runs when the PostgreSQL container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database for TaskManager (if not created by environment variable)
-- This is a backup, as the main database is created by environment variables

-- Create roles with appropriate permissions
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'taskmanager_user') THEN
        CREATE ROLE taskmanager_user LOGIN PASSWORD 'taskmanager_password';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE taskmanager TO taskmanager_user;
GRANT ALL ON SCHEMA public TO taskmanager_user;

-- Create initial tables (if using PostgreSQL instead of SQLite)
-- This is a placeholder for PostgreSQL-specific schema
-- In production, you might want to migrate the SQLite schema to PostgreSQL

COMMENT ON DATABASE taskmanager IS 'TaskManager Application Database';