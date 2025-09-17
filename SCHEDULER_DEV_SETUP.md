
# Scheduler Development Setup

## Public Scheduler Access in Development

For development convenience, the Shift Scheduler can be accessed without authentication.

### Enable Public Access

Set the environment variable:
```bash
export PUBLIC_SCHEDULER_IN_DEV=true
```

### Routes Affected

When `PUBLIC_SCHEDULER_IN_DEV=true`, these routes bypass authentication:

**Pages:**
- `/shift-scheduler` - Main scheduler page
- `/shift-scheduler/add` - Add scheduler page

**APIs:**
- `/api/shift-scheduler` - Get schedules
- `/api/shift-scheduler/save-daily-schedule` - Save schedule
- `/api/all-schedules` - Get all schedules
- `/api/staff/<id>/schedule-details` - Staff schedule details
- `/api/schedule/<id>/details` - Schedule details
- `/api/shift-scheduler/update-daily-schedule/<id>` - Update schedule
- `/api/database-records` - Database records

### Production Safety

- Default value: `false` (authentication required)
- Only affects development environment
- Production deployments should never set this flag

### Verification

Run the verification script:
```bash
python verify_scheduler_config.py
```

### Similar Flags

- `PUBLIC_STAFF_IN_DEV=true` - Bypass auth for staff management
- `PUBLIC_SCHEDULER_IN_DEV=true` - Bypass auth for scheduler (this feature)

Both flags can be used simultaneously in development.
