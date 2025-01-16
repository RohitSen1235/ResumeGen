DO $$
BEGIN
  CREATE ROLE resume WITH LOGIN PASSWORD 'postgres';
EXCEPTION WHEN duplicate_object THEN
  -- Role already exists, do nothing
  RAISE NOTICE 'Role resume already exists';
END $$;

DO $$
BEGIN
  CREATE DATABASE resume_builder OWNER resume;
EXCEPTION WHEN duplicate_database THEN
  -- Database already exists, do nothing
  RAISE NOTICE 'Database resume_builder already exists';
END $$;

GRANT ALL PRIVILEGES ON DATABASE resume_builder TO resume;
