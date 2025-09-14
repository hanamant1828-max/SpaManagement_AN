
/**
 * Add Shift Scheduler JavaScript - Day-by-Day Configuration
 * Implements the updated workflow with Generate Days functionality
 */

(function() {
    'use strict';

    // Global variables
    let currentScheduleDays = [];
    let loadingModal;

    // Initialize when document is ready
    $(document).ready(function() {
        console.log('Add Shift Scheduler JavaScript loaded');
        initializeEventHandlers();
        initializeDefaultDates();
        
        // Initialize loading modal
        loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    });

    /**
     * Initialize all event handlers
     */
    function initializeEventHandlers() {
        // Generate Days button
        $('#generateDaysBtn').on('click', generateDays);

        // Bulk action buttons
        $('#applyToAllBtn').on('click', applyToAllDays);
        $('#markWeekendsOffBtn').on('click', markWeekendsOff);
        $('#applyDefaultsBtn').on('click', applyDefaults);

        // Save schedule button
        $('#saveScheduleBtn').on('click', saveSchedule);

        // Date validation
        $('#fromDate, #toDate').on('change', validateDateRange);

        // Form validation
        $('#staffSelect, #scheduleName').on('change input', updateGenerateButton);

        // Dynamic table events (delegated)
        $('#daysConfigBody').on('change', '.working-toggle', function() {
            toggleDayWorking($(this));
        });

        $('#daysConfigBody').on('change', '.time-input, .break-input, .notes-input', function() {
            updateReviewSection();
        });
    }

    /**
     * Initialize default dates (today to next week)
     */
    function initializeDefaultDates() {
        const today = new Date();
        const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

        $('#fromDate').val(today.toISOString().split('T')[0]);
        $('#toDate').val(nextWeek.toISOString().split('T')[0]);
    }

    /**
     * Validate date range
     */
    function validateDateRange() {
        const fromDate = $('#fromDate').val();
        const toDate = $('#toDate').val();

        if (fromDate && toDate) {
            const from = new Date(fromDate);
            const to = new Date(toDate);

            if (from > to) {
                showAlert('From date cannot be after to date', 'warning');
                $('#toDate').addClass('is-invalid');
                return false;
            } else {
                $('#toDate').removeClass('is-invalid');
                return true;
            }
        }
        return true;
    }

    /**
     * Update generate button state
     */
    function updateGenerateButton() {
        const staffSelected = $('#staffSelect').val();
        const scheduleName = $('#scheduleName').val();
        const fromDate = $('#fromDate').val();
        const toDate = $('#toDate').val();

        const isValid = staffSelected && scheduleName && fromDate && toDate && validateDateRange();
        $('#generateDaysBtn').prop('disabled', !isValid);
    }

    /**
     * Generate days table based on date range
     */
    function generateDays() {
        if (!validateForm()) return;

        const fromDate = $('#fromDate').val();
        const toDate = $('#toDate').val();

        if (!fromDate || !toDate) {
            showAlert('Please select both From Date and To Date', 'warning');
            return;
        }

        if (!validateDateRange()) return;

        // Generate days array
        const days = [];
        let current = new Date(fromDate);
        const end = new Date(toDate);

        while (current <= end) {
            const dayOfWeek = current.getDay(); // 0 = Sunday, 6 = Saturday
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;

            days.push({
                date: formatDateForInput(current),
                dayName: current.toLocaleDateString('en-US', { weekday: 'long' }),
                dayOfWeek: dayOfWeek,
                working: !isWeekend, // Default: weekdays working, weekends off
                startTime: '09:00',
                endTime: '17:00',
                breakMinutes: 60,
                notes: ''
            });
            current.setDate(current.getDate() + 1);
        }

        currentScheduleDays = days;
        renderDaysConfigTable();
        
        // Show sections
        $('#dayConfigSection').slideDown(500);
        $('#reviewSection').slideDown(500);
        updateReviewSection();

        // Update day count
        $('#dayCount').text(`${days.length} days`);

        showAlert(`Generated ${days.length} days successfully!`, 'success');

        // Scroll to day config section
        setTimeout(() => {
            $('html, body').animate({
                scrollTop: $('#dayConfigSection').offset().top - 100
            }, 800);
        }, 500);
    }

    /**
     * Validate basic form
     */
    function validateForm() {
        const staffSelect = $('#staffSelect').val();
        const scheduleName = $('#scheduleName').val();
        const fromDate = $('#fromDate').val();
        const toDate = $('#toDate').val();

        if (!staffSelect) {
            showAlert('Please select a staff member', 'warning');
            return false;
        }

        if (!scheduleName) {
            showAlert('Please enter a schedule name', 'warning');
            return false;
        }

        if (!fromDate || !toDate) {
            showAlert('Please select both from and to dates', 'warning');
            return false;
        }

        return validateDateRange();
    }

    /**
     * Format date for input
     */
    function formatDateForInput(date) {
        return date.toISOString().split('T')[0];
    }

    /**
     * Format date for display
     */
    function formatDateForDisplay(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    /**
     * Render the days configuration table
     */
    function renderDaysConfigTable() {
        const tbody = $('#daysConfigBody');
        tbody.empty();

        currentScheduleDays.forEach((day, index) => {
            const row = `
                <tr class="day-config-row ${day.working ? '' : 'table-secondary'}" data-index="${index}">
                    <td class="text-center">
                        <strong>${index + 1}</strong>
                    </td>
                    <td>
                        <strong class="text-primary">${formatDateForDisplay(day.date)}</strong>
                        <br><small class="text-muted">${day.date}</small>
                    </td>
                    <td>
                        <span class="badge ${getDayBadgeClass(day.dayOfWeek)}">${day.dayName}</span>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input" 
                               data-field="startTime" data-index="${index}" 
                               value="${day.startTime}" ${day.working ? '' : 'disabled'}>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input" 
                               data-field="endTime" data-index="${index}" 
                               value="${day.endTime}" ${day.working ? '' : 'disabled'}>
                    </td>
                    <td>
                        <input type="number" class="form-control form-control-sm break-input" 
                               data-field="breakMinutes" data-index="${index}" 
                               value="${day.breakMinutes}" min="0" max="480" ${day.working ? '' : 'disabled'}>
                    </td>
                    <td class="text-center">
                        <div class="form-check form-switch">
                            <input class="form-check-input working-toggle" type="checkbox" 
                                   data-index="${index}" ${day.working ? 'checked' : ''}>
                            <label class="form-check-label text-sm">
                                ${day.working ? 'Yes' : 'No'}
                            </label>
                        </div>
                    </td>
                    <td>
                        <input type="text" class="form-control form-control-sm notes-input" 
                               data-field="notes" data-index="${index}" 
                               value="${day.notes}" placeholder="Notes..." ${day.working ? '' : 'disabled'}>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    /**
     * Get badge class for day of week
     */
    function getDayBadgeClass(dayOfWeek) {
        const classes = {
            0: 'bg-danger', // Sunday
            1: 'bg-primary', // Monday
            2: 'bg-primary', // Tuesday
            3: 'bg-primary', // Wednesday
            4: 'bg-primary', // Thursday
            5: 'bg-primary', // Friday
            6: 'bg-warning'  // Saturday
        };
        return classes[dayOfWeek] || 'bg-secondary';
    }

    /**
     * Toggle day working status
     */
    function toggleDayWorking($toggle) {
        const index = parseInt($toggle.data('index'));
        const isWorking = $toggle.is(':checked');
        
        // Update data
        currentScheduleDays[index].working = isWorking;
        
        // Update row appearance and inputs
        const $row = $toggle.closest('tr');
        const $inputs = $row.find('input:not(.working-toggle)');
        
        if (isWorking) {
            $row.removeClass('table-secondary');
            $inputs.prop('disabled', false);
            $toggle.next('label').text('Yes');
        } else {
            $row.addClass('table-secondary');
            $inputs.prop('disabled', true);
            $toggle.next('label').text('No');
        }

        updateReviewSection();
    }

    /**
     * Apply settings to all working days
     */
    function applyToAllDays() {
        const startTime = $('#defaultStartTime').val();
        const endTime = $('#defaultEndTime').val();
        const breakMinutes = $('#defaultBreak').val();

        if (!startTime || !endTime) {
            showAlert('Please set default start and end times', 'warning');
            return;
        }

        if (startTime >= endTime) {
            showAlert('End time must be after start time', 'warning');
            return;
        }

        currentScheduleDays.forEach((day, index) => {
            if (day.working) {
                day.startTime = startTime;
                day.endTime = endTime;
                day.breakMinutes = parseInt(breakMinutes);

                // Update inputs
                $(`input[data-field="startTime"][data-index="${index}"]`).val(startTime);
                $(`input[data-field="endTime"][data-index="${index}"]`).val(endTime);
                $(`input[data-field="breakMinutes"][data-index="${index}"]`).val(breakMinutes);
            }
        });

        showAlert('Settings applied to all working days', 'success');
        updateReviewSection();
    }

    /**
     * Mark weekends as non-working
     */
    function markWeekendsOff() {
        let weekendCount = 0;

        currentScheduleDays.forEach((day, index) => {
            if (day.dayOfWeek === 0 || day.dayOfWeek === 6) { // Sunday or Saturday
                day.working = false;
                weekendCount++;

                // Update checkbox
                $(`.working-toggle[data-index="${index}"]`).prop('checked', false).trigger('change');
            }
        });

        showAlert(`Marked ${weekendCount} weekend days as non-working`, 'success');
        updateReviewSection();
    }

    /**
     * Apply default values to inputs
     */
    function applyDefaults() {
        const startTime = $('#defaultStartTime').val();
        const endTime = $('#defaultEndTime').val();
        const breakMinutes = $('#defaultBreak').val();

        // Update all time inputs with defaults
        $('.time-input[data-field="startTime"]').val(startTime);
        $('.time-input[data-field="endTime"]').val(endTime);
        $('.break-input').val(breakMinutes);

        // Update data
        currentScheduleDays.forEach(day => {
            if (day.working) {
                day.startTime = startTime;
                day.endTime = endTime;
                day.breakMinutes = parseInt(breakMinutes);
            }
        });

        showAlert('Default values applied to all inputs', 'success');
        updateReviewSection();
    }

    /**
     * Update review section
     */
    function updateReviewSection() {
        const workingDays = currentScheduleDays.filter(day => day.working);
        const totalDays = currentScheduleDays.length;
        const staffName = $('#staffSelect option:selected').text();
        const scheduleName = $('#scheduleName').val();

        const summary = `
            <div class="row g-3">
                <div class="col-md-6">
                    <h6 class="text-primary"><i class="fas fa-user me-2"></i>Staff Member</h6>
                    <p class="mb-0">${staffName}</p>
                </div>
                <div class="col-md-6">
                    <h6 class="text-primary"><i class="fas fa-tag me-2"></i>Schedule Name</h6>
                    <p class="mb-0">${scheduleName}</p>
                </div>
                <div class="col-md-4">
                    <h6 class="text-success"><i class="fas fa-calendar-check me-2"></i>Total Days</h6>
                    <p class="mb-0 h5">${totalDays}</p>
                </div>
                <div class="col-md-4">
                    <h6 class="text-success"><i class="fas fa-briefcase me-2"></i>Working Days</h6>
                    <p class="mb-0 h5 text-success">${workingDays.length}</p>
                </div>
                <div class="col-md-4">
                    <h6 class="text-warning"><i class="fas fa-calendar-times me-2"></i>Non-Working Days</h6>
                    <p class="mb-0 h5 text-warning">${totalDays - workingDays.length}</p>
                </div>
            </div>
        `;

        $('#reviewSummary').html(summary);
    }

    /**
     * Save the schedule
     */
    function saveSchedule() {
        if (!validateFinalSchedule()) return;

        showLoadingModal('Saving schedule...');

        // Prepare schedule data
        const scheduleData = {
            staff_id: parseInt($('#staffSelect').val()),
            schedule_name: $('#scheduleName').val(),
            description: $('#description').val(),
            priority: parseInt($('#priority').val()),
            schedule_days: currentScheduleDays
        };

        // Send to server
        $.ajax({
            url: '/api/shift-scheduler/save-daily-schedule',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(scheduleData),
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showAlert('Schedule saved successfully!', 'success');
                    
                    // Redirect after short delay
                    setTimeout(() => {
                        window.location.href = '/shift-scheduler';
                    }, 2000);
                } else {
                    showAlert('Error saving schedule: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error saving schedule:', error);
                showAlert('Error saving schedule. Please try again.', 'danger');
            }
        });
    }

    /**
     * Validate final schedule before saving
     */
    function validateFinalSchedule() {
        const workingDays = currentScheduleDays.filter(day => day.working);
        
        if (workingDays.length === 0) {
            showAlert('At least one working day must be selected', 'warning');
            return false;
        }

        // Validate time ranges for working days
        for (let day of workingDays) {
            if (day.startTime >= day.endTime) {
                showAlert(`Invalid time range for ${day.dayName} (${day.date})`, 'warning');
                return false;
            }
        }

        return true;
    }

    /**
     * Show loading modal
     */
    function showLoadingModal(message) {
        $('#loadingMessage').text(message);
        loadingModal.show();
    }

    /**
     * Hide loading modal
     */
    function hideLoadingModal() {
        loadingModal.hide();
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

    // Update inputs when changed
    $(document).on('change', '.time-input, .break-input, .notes-input', function() {
        const $input = $(this);
        const index = parseInt($input.data('index'));
        const field = $input.data('field');
        const value = field === 'breakMinutes' ? parseInt($input.val()) : $input.val();
        
        if (currentScheduleDays[index]) {
            currentScheduleDays[index][field] = value;
            updateReviewSection();
        }
    });

    console.log('Add Shift Scheduler JavaScript fully loaded');

})();
