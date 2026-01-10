-- Add locale column to user_devices table
-- This stores the user's preferred language for push notifications

ALTER TABLE user_devices ADD COLUMN locale VARCHAR(10) DEFAULT 'en' AFTER os_version;
