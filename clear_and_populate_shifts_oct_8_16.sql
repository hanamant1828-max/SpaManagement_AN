
-- ============================================================================
-- Clear and Populate Shift Tables for October 8-16, 2025
-- ============================================================================
-- This script clears all existing shift data and creates new shifts for
-- ALL ACTIVE STAFF MEMBERS from October 8 to October 16, 2025 (9 days total)
-- Shift hours: 09:00 AM to 09:00 PM (21:00)
-- ============================================================================

-- Step 1: Disable foreign key constraints temporarily (SQLite specific)
-- This allows us to safely delete records without constraint violations
PRAGMA foreign_keys = OFF;

-- Step 2: Clear all existing shift logs
-- Delete shift_logs first since it may reference shift_management
DELETE FROM shift_logs;

-- Step 3: Clear all existing shift management records
DELETE FROM shift_management;

-- Step 4: Reset auto-increment counters for clean IDs
-- This ensures new records start from ID 1
DELETE FROM sqlite_sequence WHERE name='shift_logs';
DELETE FROM sqlite_sequence WHERE name='shift_management';

-- Step 5: Re-enable foreign key constraints
PRAGMA foreign_keys = ON;

-- ============================================================================
-- Insert Shift Management Records for ALL ACTIVE STAFF (October 8-16, 2025)
-- ============================================================================

-- Create shift management entries for all active staff members
INSERT INTO shift_management (staff_id, from_date, to_date, created_at, updated_at)
SELECT 
    id as staff_id,
    '2025-10-08' as from_date,
    '2025-10-16' as to_date,
    datetime('now') as created_at,
    datetime('now') as updated_at
FROM user
WHERE is_active = 1;

-- ============================================================================
-- Insert Shift Logs (Individual Daily Records) for ALL STAFF
-- ============================================================================
-- This creates 9 daily shift logs for each staff member

-- October 8, 2025 (Wednesday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-08' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 9, 2025 (Thursday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-09' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 10, 2025 (Friday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-10' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 11, 2025 (Saturday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-11' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 12, 2025 (Sunday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-12' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 13, 2025 (Monday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-13' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 14, 2025 (Tuesday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-14' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 15, 2025 (Wednesday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-15' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- October 16, 2025 (Thursday)
INSERT INTO shift_logs (
    shift_management_id, 
    individual_date, 
    shift_start_time, 
    shift_end_time, 
    break_start_time, 
    break_end_time,
    status,
    created_at
)
SELECT 
    sm.id as shift_management_id,
    '2025-10-16' as individual_date,
    '09:00:00' as shift_start_time,
    '21:00:00' as shift_end_time,
    '13:00:00' as break_start_time,
    '14:00:00' as break_end_time,
    'scheduled' as status,
    datetime('now') as created_at
FROM shift_management sm;

-- ============================================================================
-- Verification Queries (Optional - comment out if not needed)
-- ============================================================================
-- Uncomment the lines below to verify the data was inserted correctly

-- SELECT COUNT(*) as total_shift_management FROM shift_management;
-- SELECT COUNT(*) as total_shift_logs FROM shift_logs;
-- SELECT * FROM shift_management;
-- SELECT * FROM shift_logs ORDER BY individual_date;

-- ============================================================================
-- End of Script
-- ============================================================================
-- Summary: 
-- - Deleted all records from shift_management and shift_logs
-- - Created shift_management records for ALL ACTIVE STAFF
-- - Created 9 shift_logs records per staff member (Oct 8-16, 2025)
-- - Each shift: 09:00-21:00 with 1-hour break at 13:00-14:00
-- ============================================================================
