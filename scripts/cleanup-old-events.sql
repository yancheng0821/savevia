-- Cleanup old user_events data
-- Run this periodically to keep table size manageable
-- Recommended: Run monthly via cron or manually

-- Delete events older than 90 days
DELETE FROM user_events
WHERE created_at < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Show remaining data stats
SELECT
  COUNT(*) as remaining_rows,
  MIN(created_at) as oldest_event,
  MAX(created_at) as newest_event,
  ROUND(COUNT(*) * 100 / 1024 / 1024, 2) as estimated_size_mb
FROM user_events;

-- Optimize table to reclaim space (optional, run during low traffic)
-- OPTIMIZE TABLE user_events;
