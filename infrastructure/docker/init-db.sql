-- FinCloud Database Initialization Script
-- This script is executed when PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas for different services
CREATE SCHEMA IF NOT EXISTS budget;
CREATE SCHEMA IF NOT EXISTS portfolio;
CREATE SCHEMA IF NOT EXISTS notifications;

-- Grant permissions
GRANT ALL ON SCHEMA budget TO fincloud;
GRANT ALL ON SCHEMA portfolio TO fincloud;
GRANT ALL ON SCHEMA notifications TO fincloud;

-- Set search path
ALTER DATABASE fincloud SET search_path TO budget, portfolio, notifications, public;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'FinCloud database initialized successfully';
END $$;
