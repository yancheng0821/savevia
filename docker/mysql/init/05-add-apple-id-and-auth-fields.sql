-- Add Apple ID and authentication enhancement fields
-- Run this migration to enable Apple Sign In and password reset functionality

-- Add Apple ID support
ALTER TABLE users ADD COLUMN apple_id VARCHAR(100) UNIQUE AFTER google_id;
CREATE INDEX idx_apple_id ON users(apple_id);

-- Add email verification fields
ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT FALSE AFTER is_active;
ALTER TABLE users ADD COLUMN email_verification_token VARCHAR(100) AFTER email_verified;
ALTER TABLE users ADD COLUMN email_verification_expires_at DATETIME AFTER email_verification_token;

-- Add password reset fields
ALTER TABLE users ADD COLUMN password_reset_token VARCHAR(100) AFTER email_verification_expires_at;
ALTER TABLE users ADD COLUMN password_reset_expires_at DATETIME AFTER password_reset_token;

-- Create indexes
CREATE INDEX idx_email_verification_token ON users(email_verification_token);
CREATE INDEX idx_password_reset_token ON users(password_reset_token);
