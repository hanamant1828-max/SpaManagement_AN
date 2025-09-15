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
        loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
        
        initializeEventHandlers();
        loadSchedules();
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
            url: '/api/all-schedules',
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
                            <span class="fw-bold">${formatTime12h(schedule.shift_start_time)}</span>
                            <span class="text-muted mx-1">to</span>
                            <span class="fw-bold">${formatTime12h(schedule.shift_end_time)}</span>
                        </div>
                        ${schedule.break_time ? `<small class="text-muted d-block mt-1"><i class="fas fa-coffee me-1"></i>${schedule.break_time}</small>` : ''}
                        <div class="mt-1">
                            ${getStatusBadge(schedule.is_active)}
                        </div>
                    </td>
                    <td>
                        <div class="action-buttons-group">
                            <button type="button" class="btn action-btn-view btn-view" data-id="${schedule.id}" title="View Schedule">
                                👁 <i class="fas fa-eye"></i>
                            </button>
                            <button type="button" class="btn action-btn-edit btn-edit" data-id="${schedule.id}" title="Edit Schedule">
                                ✏ <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn action-btn-delete btn-delete" data-id="${schedule.id}" title="Delete Schedule">
                                🗑 <i class="fas fa-trash"></i>
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
     * View schedule (Page 4: View Schedule Page)
     */
    function viewSchedule(scheduleId) {
        const schedule = schedules.find(s => s.id == scheduleId);
        if (!schedule) {
            showAlert('Schedule not found', 'danger');
            return;
        }

        // Navigate to view page with schedule data in URL
        const params = new URLSearchParams({
            action: 'view',
            id: scheduleId
        });
        window.location.href = `/shift-scheduler/add?${params.toString()}`;
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
        window.location.href = `/shift-scheduler/add?${params.toString()}`;
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
            url: `/api/schedule/${scheduleId}`,
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
     * Format date for display
     */
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Invalid Date';
            }
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
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
        if (loadingModal) {
            loadingModal.hide();
        }
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

    // Make loadSchedules available globally for the template
    window.loadSchedules = loadSchedules;

    console.log('Shift Scheduler JavaScript fully loaded - Wireframe Implementation');

})();