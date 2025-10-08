
-- ============================================================================
-- Clear and Populate Shift Tables for October 8-16, 2025
-- ============================================================================
-- This script clears all existing shift data and creates new shifts for
-- each day from October 8 to October 16, 2025 (9 days total)
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
-- Insert Shift Management Records (October 8-16, 2025)
-- ============================================================================
-- Note: Assuming staff_id exists in your database. Replace '1' with actual staff IDs
-- If you have multiple staff members, duplicate these INSERTs with different staff_ids

-- Insert shift management for staff member 1
INSERT INTO shift_management (staff_id, from_date, to_date, created_at, updated_at) 
VALUES (1, '2025-10-08', '2025-10-16', datetime('now'), datetime('now'));

-- ============================================================================
-- Insert Shift Logs (Individual Daily Records)
-- ============================================================================
-- Each log represents one working day with shift details
-- shift_management_id references the record created above (ID will be 1)

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
) VALUES (
    1,                      -- References shift_management with ID 1
    '2025-10-08',          -- Wednesday
    '09:00:00',            -- 9:00 AM
    '21:00:00',            -- 9:00 PM
    '13:00:00',            -- Break start: 1:00 PM
    '14:00:00',            -- Break end: 2:00 PM
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-09',          -- Thursday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-10',          -- Friday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-11',          -- Saturday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-12',          -- Sunday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-13',          -- Monday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-14',          -- Tuesday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-15',          -- Wednesday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
) VALUES (
    1,
    '2025-10-16',          -- Thursday
    '09:00:00',
    '21:00:00',
    '13:00:00',
    '14:00:00',
    'scheduled',
    datetime('now')
);

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
-- - Created 1 shift_management record for staff_id=1
-- - Created 9 shift_logs records (Oct 8-16, 2025)
-- - Each shift: 09:00-21:00 with 1-hour break at 13:00-14:00
-- ============================================================================
