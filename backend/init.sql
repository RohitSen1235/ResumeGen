DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'resume') THEN
    CREATE ROLE resume WITH LOGIN PASSWORD 'postgres';
  END IF;
END $$;
CREATE DATABASE resume_builder OWNER resume;
