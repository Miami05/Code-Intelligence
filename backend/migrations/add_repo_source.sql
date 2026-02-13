-- Migration: Add source column to repositories table
-- Sprint 6: GitHub Integration

-- Add source column with default value
ALTER TABLE repositories 
ADD COLUMN IF NOT EXISTS source VARCHAR(20) DEFAULT 'upload' NOT NULL;

-- Create enum type if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reposource') THEN
        CREATE TYPE reposource AS ENUM ('upload', 'github');
    END IF;
END $$;

-- Update column to use enum type
ALTER TABLE repositories 
ALTER COLUMN source TYPE reposource USING source::reposource;

-- Update existing GitHub repos to have source='github'
UPDATE repositories 
SET source = 'github' 
WHERE github_url IS NOT NULL;

-- Add index on source column
CREATE INDEX IF NOT EXISTS idx_repositories_source ON repositories(source);

-- Verify
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE source = 'github') as github_repos,
    COUNT(*) FILTER (WHERE source = 'upload') as upload_repos
FROM repositories;
