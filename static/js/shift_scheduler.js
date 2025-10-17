/**
 * Shift Scheduler JavaScript - Wireframe Implementation
 * Clean page-based navigation: View -> Add -> Edit -> View -> Delete
 */

(function() {
    'use strict';

    // Global variables
    let schedules = [];
    let loadingModal;

    // Initialize when document is ready
    $(document).ready(function() {
        console.log('Shift Scheduler JavaScript loaded - Wireframe Implementation');
        
        // Initialize loading modal first
        const modalElement = document.getElementById('loadingModal');
        if (modalElement) {
            loadingModal = new bootstrap.Modal(modalElement, {
                backdrop: 'static',
                keyboard: false
            });
        }
        
        initializeEventHandlers();
        
        // Add a small delay to ensure DOM is fully ready
        setTimeout(() => {
            loadSchedules();
        }, 100);
    });

    /**
     * Initialize all event handlers
     */
    function initializeEventHandlers() {
        // Refresh schedules button
        $('#refreshSchedulesBtn').on('click', function() {
            loadSchedules();
        });

        // Delegated event handlers for dynamic buttons
        $(document).on('click', '.btn-view', function() {
            const scheduleId = $(this).data('id');
            viewSchedule(scheduleId);
        });

        $(document).on('click', '.btn-edit', function() {
            const scheduleId = $(this).data('id');
            editSchedule(scheduleId);
        });

        $(document).on('click', '.btn-delete', function() {
            const scheduleId = $(this).data('id');
            deleteSchedule(scheduleId);
        });
    }

    /**
     * Load all schedules from server
     */
    function loadSchedules() {
        showLoadingModal('Loading schedules...');

        $.ajax({
            url: '/shift-scheduler/api/all-schedules',
            method: 'GET',
            success: function(response) {
                hideLoadingModal();
                console.log('API Response:', response);
                if (response.success) {
                    schedules = response.schedules || [];
                    console.log('Loaded schedules:', schedules);
                    renderScheduleTable();
                    updateScheduleCount();
                } else {
                    console.error('API Error:', response.error);
                    showAlert('Error loading schedules: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('AJAX Error:', {
                    status: status,
                    error: error,
                    responseText: xhr.responseText,
                    statusCode: xhr.status
                });
                showAlert('Error loading schedules. Please try again.', 'danger');
            },
            complete: function() {
                // Ensure modal is hidden even if there's an unexpected issue
                hideLoadingModal();
            }
        });
    }

    /**
     * Render the schedule table
     */
    function renderScheduleTable() {
        const tbody = $('#scheduleTableBody');
        const noSchedules = $('#noSchedules');

        tbody.empty();

        if (schedules.length === 0) {
            noSchedules.show();
            return;
        }

        noSchedules.hide();

        schedules.forEach((schedule, index) => {
            const row = `
                <tr class="schedule-row" data-id="${schedule.id}">
                    <td class="text-center">
                        <strong class="text-primary">${index + 1}</strong>
                    </td>
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="bg-primary bg-opacity-10 rounded-circle p-2 me-3">
                                <i class="fas fa-user text-primary"></i>
                            </div>
                            <div>
                                <strong class="text-dark">${schedule.staff_name}</strong>
                                <br><small class="text-muted">${schedule.schedule_name || 'Schedule'}</small>
                            </div>
                        </div>
                    </td>
                    <td>
                        <span class="date-display">${formatDate(schedule.start_date)}</span>
                    </td>
                    <td>
                        <span class="date-display">${formatDate(schedule.end_date)}</span>
                    </td>
                    <td>
                        <span class="badge-office-days">
                            <i class="fas fa-calendar-week me-1"></i>${schedule.working_days_str}
                        </span>
                    </td>
                    <td>
                        <div class="time-range">
                            <i class="fas fa-clock me-1"></i>
                            <span class="fw-bold">${convert24To12Hour(schedule.shift_start_time)}</span>
                            <span class="text-muted mx-1">to</span>
                            <span class="fw-bold">${convert24To12Hour(schedule.shift_end_time)}</span>
                        </div>
                        ${schedule.break_time ? `<small class="text-muted d-block mt-1"><i class="fas fa-coffee me-1"></i>${schedule.break_time}</small>` : ''}
                    </td>
                    <td class="text-center">
                        ${getStatusBadge(schedule.is_active)}
                    </td>
                    <td class="text-center">
                        <div class="action-buttons-group">
                            <button type="button" class="btn action-btn-view btn-view" data-id="${schedule.id}" title="View Schedule">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button type="button" class="btn action-btn-edit btn-edit" data-id="${schedule.id}" title="Edit Schedule">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn action-btn-delete btn-delete" data-id="${schedule.id}" title="Delete Schedule">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    /**
     * Update schedule count badge
     */
    function updateScheduleCount() {
        $('#scheduleCount').text(schedules.length);
    }

    /**
     * View schedule (Show detailed modal with all daily schedules)
     */
    function viewSchedule(scheduleId) {
        const schedule = schedules.find(s => s.id == scheduleId);
        if (!schedule) {
            showAlert('Schedule not found', 'danger');
            return;
        }

        showLoadingModal('Loading schedule details...');

        // Get comprehensive schedule details
        $.ajax({
            url: `/shift-scheduler/api/staff/${schedule.staff_id}/schedule-details`,
            method: 'GET',
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showScheduleDetailsModal(response);
                } else {
                    showAlert('Error loading schedule details: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error loading schedule details:', error);
                showAlert('Error loading schedule details. Please try again.', 'danger');
            }
        });
    }

    /**
     * Edit schedule (Page 3: Edit Schedule Page)
     */
    function editSchedule(scheduleId) {
        const schedule = schedules.find(s => s.id == scheduleId);
        if (!schedule) {
            showAlert('Schedule not found', 'danger');
            return;
        }

        // Navigate to edit page with schedule data in URL
        const params = new URLSearchParams({
            action: 'edit',
            id: scheduleId
        });
        window.location.href = `/shift-scheduler/shift-scheduler/add?${params.toString()}`;
    }

    /**
     * Delete schedule (Page 5: Delete Action)
     */
    function deleteSchedule(scheduleId) {
        const schedule = schedules.find(s => s.id == scheduleId);
        if (!schedule) {
            showAlert('Schedule not found', 'danger');
            return;
        }

        // Show confirmation dialog
        if (!confirm(`Are you sure you want to delete the schedule for ${schedule.staff_name}?\n\nFrom: ${formatDate(schedule.start_date)}\nTo: ${formatDate(schedule.end_date)}\n\nThis action cannot be undone.`)) {
            return;
        }

        showLoadingModal('Deleting schedule...');

        $.ajax({
            url: `/shift-scheduler/api/schedule/${scheduleId}`,
            method: 'DELETE',
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showAlert('Schedule deleted successfully!', 'success');
                    loadSchedules(); // Refresh the table
                } else {
                    showAlert('Error deleting schedule: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error deleting schedule:', error);
                showAlert('Error deleting schedule. Please try again.', 'danger');
            }
        });
    }

    /**
     * Format date for display in Indian format (DD-MM-YYYY)
     */
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Invalid Date';
            }
            const day = String(date.getDate()).padStart(2, '0');
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const year = date.getFullYear();
            return `${day}-${month}-${year}`;
        } catch (e) {
            console.error("Error formatting date:", dateString, e);
            return 'Error';
        }
    }

    /**
     * Format time from 24-hour to 12-hour format
     */
    function formatTime12h(timeString) {
        if (!timeString) return 'N/A';
        try {
            // Parse HH:MM format
            const [hours, minutes] = timeString.split(':');
            if (!hours || !minutes) return timeString;
            
            const hour24 = parseInt(hours, 10);
            const min = parseInt(minutes, 10);
            
            if (isNaN(hour24) || isNaN(min)) return timeString;
            
            const hour12 = hour24 === 0 ? 12 : (hour24 > 12 ? hour24 - 12 : hour24);
            const ampm = hour24 >= 12 ? 'PM' : 'AM';
            
            return `${hour12}:${min.toString().padStart(2, '0')} ${ampm}`;
        } catch (error) {
            console.error('Time formatting error:', error);
            return timeString;
        }
    }

    /**
     * Convert 24-hour time to 12-hour format with AM/PM
     */
    function convert24To12Hour(time24) {
        if (!time24) return '';
        
        try {
            const [hours, minutes] = time24.split(':');
            const hour24 = parseInt(hours, 10);
            const min = parseInt(minutes, 10);
            
            if (isNaN(hour24) || isNaN(min)) return time24;
            
            const hour12 = hour24 === 0 ? 12 : (hour24 > 12 ? hour24 - 12 : hour24);
            const ampm = hour24 >= 12 ? 'PM' : 'AM';
            
            return `${hour12}:${min.toString().padStart(2, '0')} ${ampm}`;
        } catch (error) {
            console.error('Time conversion error:', error);
            return time24;
        }
    }

    /**
     * Generate status badge HTML based on active status
     */
    function getStatusBadge(isActive) {
        // Default to active if status is undefined/null
        if (isActive !== false) {
            return '<span class="badge bg-success">Active</span>';
        } else {
            return '<span class="badge bg-secondary">Inactive</span>';
        }
    }

    /**
     * Show loading modal
     */
    function showLoadingModal(message) {
        $('#loadingMessage').text(message);
        if (loadingModal) {
            loadingModal.show();
        }
    }

    /**
     * Hide loading modal
     */
    function hideLoadingModal() {
        try {
            // Try Bootstrap 5 instance method first
            if (loadingModal) {
                loadingModal.hide();
            }
            
            // Ensure modal element is hidden
            const modalElement = document.getElementById('loadingModal');
            if (modalElement) {
                modalElement.classList.remove('show');
                modalElement.style.display = 'none';
                modalElement.setAttribute('aria-hidden', 'true');
            }
            
            // Remove any backdrop
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                backdrop.remove();
            });
            
            // Restore body scroll
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
        } catch (e) {
            console.error('Error hiding loading modal:', e);
        }
    }

    /**
     * Show detailed schedule modal
     */
    function showScheduleDetailsModal(data) {
        const staff = data.staff;
        const ranges = data.schedule_ranges;
        const dailySchedules = data.daily_schedules;

        // Group daily schedules by range
        const schedulesByRange = {};
        dailySchedules.forEach(daily => {
            if (!schedulesByRange[daily.range_id]) {
                schedulesByRange[daily.range_id] = [];
            }
            schedulesByRange[daily.range_id].push(daily);
        });

        let modalContent = `
            <div class="modal fade" id="scheduleDetailsModal" tabindex="-1" aria-labelledby="scheduleDetailsModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="scheduleDetailsModalLabel">
                                <i class="fas fa-calendar-check me-2"></i>
                                Schedule Details - ${staff.name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-12">
                                    <h6 class="mb-3">
                                        <i class="fas fa-info-circle me-2"></i>
                                        Staff Information
                                    </h6>
                                    <div class="card mb-4">
                                        <div class="card-body">
                                            <p><strong>Name:</strong> ${staff.name}</p>
                                            <p><strong>Role:</strong> ${staff.role}</p>
                                            <p><strong>Total Schedule Ranges:</strong> ${ranges.length}</p>
                                            <p><strong>Total Days Scheduled:</strong> ${dailySchedules.length}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
        `;

        // Add schedule ranges
        ranges.forEach(range => {
            const rangeDays = schedulesByRange[range.id] || [];
            
            modalContent += `
                <div class="mb-4">
                    <h6 class="mb-3">
                        <i class="fas fa-calendar-alt me-2"></i>
                        ${range.schedule_name}
                    </h6>
                    <div class="card">
                        <div class="card-header">
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Period:</strong> ${formatDate(range.start_date)} to ${formatDate(range.end_date)}
                                </div>
                                <div class="col-md-6">
                                    <strong>Shift Times:</strong> ${range.shift_start_time_12h} - ${range.shift_end_time_12h}
                                </div>
                            </div>
                            <div class="row mt-2">
                                <div class="col-md-6">
                                    <strong>Working Days:</strong> ${range.working_days_str}
                                </div>
                                <div class="col-md-6">
                                    <strong>Break Time:</strong> ${range.break_time || 'Not specified'}
                                </div>
                            </div>
                            ${range.description ? `<div class="mt-2"><strong>Description:</strong> ${range.description}</div>` : ''}
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-sm table-striped mb-0">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Date</th>
                                            <th>Day</th>
                                            <th>Working</th>
                                            <th>Start Time</th>
                                            <th>End Time</th>
                                            <th>Break</th>
                                            <th>Notes</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            `;

            if (rangeDays.length > 0) {
                rangeDays.forEach(day => {
                    modalContent += `
                        <tr class="${day.is_working ? '' : 'table-secondary'}">
                            <td>${formatDate(day.date)}</td>
                            <td>${day.day_name}</td>
                            <td>
                                ${day.is_working ? 
                                    '<span class="badge bg-success">Yes</span>' : 
                                    '<span class="badge bg-secondary">Off</span>'
                                }
                            </td>
                            <td>${day.is_working ? (day.start_time_12h || 'N/A') : '-'}</td>
                            <td>${day.is_working ? (day.end_time_12h || 'N/A') : '-'}</td>
                            <td>
                                ${day.is_working ? (day.break_time_display || 'No break') : '-'}
                                ${day.out_of_office_display ? '<br><small class="text-warning"><i class="fas fa-briefcase"></i> Out: ' + day.out_of_office_display + '</small>' : ''}
                            </td>
                            <td>${day.notes || '-'}</td>
                        </tr>
                    `;
                });
            } else {
                modalContent += `
                    <tr>
                        <td colspan="7" class="text-center text-muted">
                            No daily schedule entries found for this range
                        </td>
                    </tr>
                `;
            }

            modalContent += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        modalContent += `
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        $('#scheduleDetailsModal').remove();
        
        // Add modal to body and show
        $('body').append(modalContent);
        const modal = new bootstrap.Modal(document.getElementById('scheduleDetailsModal'));
        modal.show();
    }

    /**
     * View database records - shows SQL INSERT statements
     */
    function viewDatabaseRecords() {
        showLoadingModal('Loading database records...');

        $.ajax({
            url: '/shift-scheduler/api/database-records',
            method: 'GET',
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showDatabaseRecordsModal(response);
                } else {
                    showAlert('Error loading database records: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error loading database records:', error);
                showAlert('Error loading database records. Please try again.', 'danger');
            }
        });
    }

    /**
     * Show database records modal with SQL statements
     */
    function showDatabaseRecordsModal(data) {
        let modalContent = `
            <div class="modal fade" id="databaseRecordsModal" tabindex="-1" aria-labelledby="databaseRecordsModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="databaseRecordsModalLabel">
                                <i class="fas fa-database me-2"></i>
                                Database Records - SQL INSERT Statements
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="alert alert-info">
                                <strong>Summary:</strong> ${data.summary}
                            </div>
                            
                            <!-- Shift Management Records -->
                            <h6 class="mb-3">
                                <i class="fas fa-table me-2"></i>
                                shift_management table (${data.total_management_records} records):
                            </h6>
                            <div class="card mb-4">
                                <div class="card-body">
        `;

        data.management_records.forEach((record, index) => {
            modalContent += `
                <div class="mb-3">
                    <strong>Record ${index + 1}:</strong>
                    <div class="bg-light p-3 mt-2" style="font-family: 'Courier New', monospace; font-size: 0.9em;">
                        <code>${record.sql_statement}</code>
                    </div>
                    <small class="text-muted">
                        -- Staff: ${record.record_data.staff_name} | Period: ${record.record_data.from_date} to ${record.record_data.to_date}
                    </small>
                </div>
            `;
        });

        modalContent += `
                                </div>
                            </div>

                            <!-- Shift Logs Records -->
                            <h6 class="mb-3">
                                <i class="fas fa-calendar me-2"></i>
                                shift_logs table (${data.total_log_records} records - individual working days):
                            </h6>
                            <div class="card mb-4">
                                <div class="card-body">
        `;

        data.log_records.forEach((record, index) => {
            modalContent += `
                <div class="mb-3">
                    <strong>${record.record_data.day_name}, ${record.record_data.individual_date}:</strong>
                    <div class="bg-light p-3 mt-2" style="font-family: 'Courier New', monospace; font-size: 0.9em;">
                        <code>${record.sql_statement}</code>
                    </div>
                    <small class="text-muted">
                        -- Shift: ${record.record_data.shift_start_time} to ${record.record_data.shift_end_time} | 
                        Break: ${record.record_data.break_start_time || 'None'} to ${record.record_data.break_end_time || 'None'}
                    </small>
                </div>
            `;
        });

        modalContent += `
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal if any
        $('#databaseRecordsModal').remove();
        
        // Add modal to body and show
        $('body').append(modalContent);
        const modal = new bootstrap.Modal(document.getElementById('databaseRecordsModal'));
        modal.show();
    }

    /**
     * Show alert message
     */
    function showAlert(message, type = 'success') {
        const alertClass = type === 'danger' ? 'alert-danger' : 
                          type === 'warning' ? 'alert-warning' :
                          type === 'info' ? 'alert-info' : 'alert-success';
        const iconClass = type === 'danger' ? 'fa-exclamation-triangle' : 
                         type === 'warning' ? 'fa-exclamation-circle' :
                         type === 'info' ? 'fa-info-circle' : 'fa-check-circle';

        const alertHtml = `
            <div class="alert ${alertClass} alert-dismissible fade show slide-in" role="alert" style="margin: 1rem 0;">
                <div class="d-flex align-items-center">
                    <i class="fas ${iconClass} me-3" style="font-size: 1.2em;"></i>
                    <div class="flex-grow-1">${message}</div>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            </div>
        `;

        $('.container-fluid').prepend(alertHtml);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            $('.alert').first().fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    }

    // Make functions available globally for the template
    window.loadSchedules = loadSchedules;
    window.viewDatabaseRecords = viewDatabaseRecords;
    window.openOutOfOfficeModal = openOutOfOfficeModal;
    window.resetOutOfOfficeForm = resetOutOfOfficeForm;
    window.editOutOfOfficeEntry = editOutOfOfficeEntry;
    window.deleteOutOfOfficeEntry = deleteOutOfOfficeEntry;

    /**
     * Open Out of Office modal and load entries
     */
    function openOutOfOfficeModal() {
        resetOutOfOfficeForm();
        loadOutOfOfficeEntries();
        const modal = new bootstrap.Modal(document.getElementById('outOfOfficeModal'));
        modal.show();
    }

    /**
     * Load all out of office entries
     */
    function loadOutOfOfficeEntries() {
        $.ajax({
            url: '/shift-scheduler/api/out-of-office',
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    renderOutOfOfficeTable(response.entries);
                } else {
                    showAlert('Error loading entries: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading out of office entries:', error);
                showAlert('Error loading entries. Please try again.', 'danger');
            }
        });
    }

    /**
     * Render out of office entries table
     */
    function renderOutOfOfficeTable(entries) {
        const tbody = $('#outOfOfficeTableBody');
        tbody.empty();

        if (entries.length === 0) {
            tbody.append('<tr><td colspan="6" class="text-center text-muted">No entries found</td></tr>');
            return;
        }

        entries.forEach(entry => {
            const row = `
                <tr>
                    <td>${entry.staff_name}</td>
                    <td>${formatDate(entry.date)}</td>
                    <td>${convert24To12Hour(entry.start_time)} - ${convert24To12Hour(entry.end_time)}</td>
                    <td>${entry.duration_minutes} min</td>
                    <td>${entry.reason}</td>
                    <td>
                        <button class="btn btn-sm btn-primary" onclick="editOutOfOfficeEntry(${entry.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteOutOfOfficeEntry(${entry.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    /**
     * Reset out of office form
     */
    function resetOutOfOfficeForm() {
        $('#outOfOfficeForm')[0].reset();
        $('#outOfOfficeId').val('');
        $('#shiftLogId').val('');
        $('#outOfOfficeFormTitle').text('Add Out of Office Entry');
    }

    /**
     * Edit out of office entry
     */
    function editOutOfOfficeEntry(id) {
        $.ajax({
            url: `/shift-scheduler/api/out-of-office/${id}`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const entry = response.entry;
                    $('#outOfOfficeId').val(entry.id);
                    $('#shiftLogId').val(entry.shift_log_id);
                    $('#outStaffId').val(entry.staff_id);
                    $('#outDate').val(entry.date);
                    $('#outReason').val(entry.reason);
                    $('#outStartTime').val(entry.start_time);
                    $('#outEndTime').val(entry.end_time);
                    $('#outOfOfficeFormTitle').text('Edit Out of Office Entry');
                } else {
                    showAlert('Error loading entry: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error loading entry:', error);
                showAlert('Error loading entry. Please try again.', 'danger');
            }
        });
    }

    /**
     * Delete out of office entry
     */
    function deleteOutOfOfficeEntry(id) {
        if (!confirm('Are you sure you want to delete this entry?')) {
            return;
        }

        $.ajax({
            url: `/shift-scheduler/api/out-of-office/${id}`,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    showAlert('Entry deleted successfully!', 'success');
                    loadOutOfOfficeEntries();
                } else {
                    showAlert('Error deleting entry: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error deleting entry:', error);
                showAlert('Error deleting entry. Please try again.', 'danger');
            }
        });
    }

    /**
     * Handle out of office form submission
     */
    $('#outOfOfficeForm').on('submit', function(e) {
        e.preventDefault();

        const entryId = $('#outOfOfficeId').val();
        const data = {
            staff_id: parseInt($('#outStaffId').val()),
            date: $('#outDate').val(),
            reason: $('#outReason').val(),
            start_time: $('#outStartTime').val(),
            end_time: $('#outEndTime').val()
        };

        const url = entryId ? `/shift-scheduler/api/out-of-office/${entryId}` : '/shift-scheduler/api/out-of-office';
        const method = entryId ? 'PUT' : 'POST';

        $.ajax({
            url: url,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.success) {
                    showAlert(entryId ? 'Entry updated successfully!' : 'Entry added successfully!', 'success');
                    resetOutOfOfficeForm();
                    loadOutOfOfficeEntries();
                } else {
                    showAlert('Error saving entry: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                console.error('Error saving entry:', error);
                showAlert('Error saving entry. Please try again.', 'danger');
            }
        });
    });

    console.log('Shift Scheduler JavaScript fully loaded - Wireframe Implementation');

})();