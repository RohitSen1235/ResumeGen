DO $$
BEGIN
  CREATE ROLE resume WITH LOGIN PASSWORD 'postgres';
EXCEPTION WHEN duplicate_object THEN
  -- Role already exists, do nothing
  RAISE NOTICE 'Role resume already exists';
END $$;

CREATE DATABASE resume_builder OWNER resume;

GRANT ALL PRIVILEGES ON DATABASE resume_builder TO resume;
