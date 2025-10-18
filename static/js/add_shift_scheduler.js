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

        // Check if we're in view/edit mode and load existing data
        const urlParams = new URLSearchParams(window.location.search);
        const action = urlParams.get('action');
        const scheduleId = urlParams.get('id');

        if (action && scheduleId && (action === 'view' || action === 'edit')) {
            loadExistingSchedule(action, scheduleId);
        }
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

        // Default time input change handlers
        $('#defaultStartTime').on('change', function() {
            updateDefaultTimeDisplays();
        });
        $('#defaultEndTime').on('change', function() {
            updateDefaultTimeDisplays();
        });
        $('#defaultBreakStart').on('change', function() {
            updateDefaultTimeDisplays();
            updateDefaultBreakMinutes();
        });
        $('#defaultBreakEnd').on('change', function() {
            updateDefaultTimeDisplays();
            updateDefaultBreakMinutes();
        });
    }

    /**
     * Initialize default dates (today to next week)
     */
    function initializeDefaultDates() {
        const today = new Date();
        const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

        $('#fromDate').val(formatDateForInput(today));
        $('#toDate').val(formatDateForInput(nextWeek));
        updateGenerateButton(); // Ensure button is enabled if defaults are valid
    }

    /**
     * Update default time and break displays
     */
    function updateDefaultTimeDisplays() {
        $('#defaultStartTimeDisplay').text(convert24To12Hour($('#defaultStartTime').val()));
        $('#defaultEndTimeDisplay').text(convert24To12Hour($('#defaultEndTime').val()));
        $('#defaultBreakStartDisplay').text(convert24To12Hour($('#defaultBreakStart').val()));
        $('#defaultBreakEndDisplay').text(convert24To12Hour($('#defaultBreakEnd').val()));
    }

    /**
     * Update default break minutes based on selected break times
     */
    function updateDefaultBreakMinutes() {
        const breakStart = $('#defaultBreakStart').val();
        const breakEnd = $('#defaultBreakEnd').val();
        const breakMinutes = calculateBreakMinutes(breakStart, breakEnd);
        $('#defaultBreak').val(breakMinutes);
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
                breakStart: '13:00',
                breakEnd: '14:00',
                breakMinutes: 60,
                outOfOfficeStart: '',
                outOfOfficeEnd: '',
                outOfOfficeMinutes: 0,
                outOfOfficeReason: '',
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
        const d = new Date(date);
        const month = (d.getMonth() + 1).toString().padStart(2, '0');
        const day = d.getDate().toString().padStart(2, '0');
        return `${d.getFullYear()}-${month}-${day}`;
    }

    /**
     * Format date for display in Indian format (DD-MM-YYYY with day name)
     */
    function formatDateForDisplay(dateString) {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
        const dayName = dayNames[date.getDay()];
        return `${dayName}, ${day}-${month}-${year}`;
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
                    <td class="text-center align-middle">
                        <strong>${index + 1}</strong>
                    </td>
                    <td class="align-middle">
                        <strong class="text-primary">${formatDateForDisplay(day.date)}</strong>
                        <br><small class="text-muted">${day.date}</small>
                    </td>
                    <td class="align-middle">
                        <span class="badge ${getDayBadgeClass(day.dayOfWeek)}">${day.dayName}</span>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input"
                               data-field="startTime" data-index="${index}"
                               value="${day.startTime}" ${day.working ? '' : 'disabled'}>
                        <small class="text-muted d-block">${convert24To12Hour(day.startTime)}</small>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input"
                               data-field="endTime" data-index="${index}"
                               value="${day.endTime}" ${day.working ? '' : 'disabled'}>
                        <small class="text-muted d-block">${convert24To12Hour(day.endTime)}</small>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input break-start"
                               data-field="breakStart" data-index="${index}"
                               value="${day.breakStart}" ${day.working ? '' : 'disabled'} onchange="updateBreakTime(this)">
                        <small class="text-muted d-block">${convert24To12Hour(day.breakStart)}</small>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input break-end"
                               data-field="breakEnd" data-index="${index}"
                               value="${day.breakEnd}" ${day.working ? '' : 'disabled'} onchange="updateBreakTime(this)">
                        <small class="text-muted d-block">${convert24To12Hour(day.breakEnd)}</small>
                    </td>
                    <td>
                        <input type="number" class="form-control form-control-sm break-input"
                               data-field="breakMinutes" data-index="${index}"
                               value="${day.breakMinutes}" min="0" max="480" ${day.working ? '' : 'disabled'} readonly>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input out-start"
                               data-field="outOfOfficeStart" data-index="${index}"
                               value="${day.outOfOfficeStart || ''}" ${day.working ? '' : 'disabled'} onchange="updateOutOfOfficeTime(this)">
                        <small class="text-muted d-block">${day.outOfOfficeStart ? convert24To12Hour(day.outOfOfficeStart) : ''}</small>
                    </td>
                    <td>
                        <input type="time" class="form-control form-control-sm time-input out-end"
                               data-field="outOfOfficeEnd" data-index="${index}"
                               value="${day.outOfOfficeEnd || ''}" ${day.working ? '' : 'disabled'} onchange="updateOutOfOfficeTime(this)">
                        <small class="text-muted d-block">${day.outOfOfficeEnd ? convert24To12Hour(day.outOfOfficeEnd) : ''}</small>
                    </td>
                    <td>
                        <input type="number" class="form-control form-control-sm out-minutes"
                               data-field="outOfOfficeMinutes" data-index="${index}"
                               value="${day.outOfOfficeMinutes || 0}" min="0" max="480" ${day.working ? '' : 'disabled'} readonly>
                    </td>
                    <td>
                        <input type="text" class="form-control form-control-sm"
                               data-field="outOfOfficeReason" data-index="${index}"
                               value="${day.outOfOfficeReason || ''}" placeholder="Reason..." ${day.working ? '' : 'disabled'}>
                    </td>
                    <td class="text-center align-middle">
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
        const breakStart = $('#defaultBreakStart').val();
        const breakEnd = $('#defaultBreakEnd').val();

        if (!startTime || !endTime) {
            showAlert('Please set default start and end times', 'warning');
            return;
        }

        if (startTime >= endTime) {
            showAlert('End time must be after start time', 'warning');
            return;
        }

        if (breakStart && breakEnd && breakStart >= breakEnd) {
            showAlert('Break end time must be after break start time', 'warning');
            return;
        }

        // Calculate break minutes
        const breakMinutes = calculateBreakMinutes(breakStart, breakEnd);

        currentScheduleDays.forEach((day, index) => {
            if (day.working) {
                day.startTime = startTime;
                day.endTime = endTime;
                day.breakStart = breakStart;
                day.breakEnd = breakEnd;
                day.breakMinutes = breakMinutes;

                // Update inputs
                const $row = $(`tr[data-index="${index}"]`);
                $row.find('input[data-field="startTime"]').val(startTime);
                $row.find('input[data-field="endTime"]').val(endTime);
                $row.find('input[data-field="breakStart"]').val(breakStart);
                $row.find('input[data-field="breakEnd"]').val(breakEnd);
                $row.find('input[data-field="breakMinutes"]').val(breakMinutes);

                // Update the 12-hour displays
                updateTimeDisplay($row.find('input[data-field="startTime"]'));
                updateTimeDisplay($row.find('input[data-field="endTime"]'));
                updateTimeDisplay($row.find('input[data-field="breakStart"]'));
                updateTimeDisplay($row.find('input[data-field="breakEnd"]'));
            }
        });

        showAlert('Settings applied to all working days', 'success');
        updateReviewSection();
    }

    /**
     * Calculate break minutes from start and end times
     */
    function calculateBreakMinutes(startTime, endTime) {
        if (!startTime || !endTime) return 0;

        const start = new Date(`2000-01-01T${startTime}:00`);
        const end = new Date(`2000-01-01T${endTime}:00`);

        const diffMs = end - start;
        const diffMinutes = Math.floor(diffMs / (1000 * 60));

        return diffMinutes > 0 ? diffMinutes : 0;
    }

    /**
     * Mark weekends as non-working
     */
    function markWeekendsOff() {
        let weekendCount = 0;

        currentScheduleDays.forEach((day, index) => {
            if (day.dayOfWeek === 0 || day.dayOfWeek === 6) { // Sunday or Saturday
                if (day.working) { // Only count if it was previously working
                    day.working = false;
                    weekendCount++;

                    // Update checkbox and row appearance
                    const $toggle = $(`.working-toggle[data-index="${index}"]`);
                    $toggle.prop('checked', false).trigger('change');
                }
            }
        });

        if (weekendCount > 0) {
            showAlert(`Marked ${weekendCount} weekend days as non-working`, 'success');
        } else {
            showAlert('No working weekend days found to mark off', 'info');
        }
        updateReviewSection();
    }

    /**
     * Apply default values to inputs
     */
    function applyDefaults() {
        const defaultStart = $('#defaultStartTime').val();
        const defaultEnd = $('#defaultEndTime').val();
        const defaultBreakStart = $('#defaultBreakStart').val();
        const defaultBreakEnd = $('#defaultBreakEnd').val();
        const defaultBreak = $('#defaultBreak').val();

        $('#daysConfigBody tr').each(function() {
            const $row = $(this);
            const workingCheckbox = $row.find('.working-toggle');

            if (workingCheckbox.is(':checked')) {
                // Update input values
                $row.find('.time-input[data-field="startTime"]').val(defaultStart);
                $row.find('.time-input[data-field="endTime"]').val(defaultEnd);
                $row.find('.time-input[data-field="breakStart"]').val(defaultBreakStart);
                $row.find('.time-input[data-field="breakEnd"]').val(defaultBreakEnd);
                $row.find('.break-input').val(defaultBreak);

                // Update data array
                const index = parseInt($row.data('index'));
                currentScheduleDays[index].startTime = defaultStart;
                currentScheduleDays[index].endTime = defaultEnd;
                currentScheduleDays[index].breakStart = defaultBreakStart;
                currentScheduleDays[index].breakEnd = defaultBreakEnd;
                currentScheduleDays[index].breakMinutes = parseInt(defaultBreak);

                // Update time displays
                updateTimeDisplay($row.find('.time-input[data-field="startTime"]'));
                updateTimeDisplay($row.find('.time-input[data-field="endTime"]'));
                updateTimeDisplay($row.find('.time-input[data-field="breakStart"]'));
                updateTimeDisplay($row.find('.time-input[data-field="breakEnd"]'));
            }
        });

        showAlert('Default values applied to all working days', 'success');
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
        const scheduleData = [];
        currentScheduleDays.forEach((day) => {
            if (day.working) {
                scheduleData.push({
                    date: day.date,
                    working: day.working,
                    startTime: day.startTime,
                    endTime: day.endTime,
                    breakStart: day.breakStart,
                    breakEnd: day.breakEnd,
                    breakMinutes: day.breakMinutes,
                    outOfOfficeStart: day.outOfOfficeStart || '',
                    outOfOfficeEnd: day.outOfOfficeEnd || '',
                    outOfOfficeMinutes: day.outOfOfficeMinutes || 0,
                    outOfOfficeReason: day.outOfOfficeReason || '',
                    notes: day.notes
                });
            }
        });

        const requestData = {
            staff_id: parseInt($('#staffSelect').val()),
            schedule_name: $('#scheduleName').val(),
            description: $('#description').val(),
            priority: parseInt($('#priority').val()),
            schedule_days: scheduleData
        };

        // Check if we're in edit mode
        const urlParams = new URLSearchParams(window.location.search);
        const action = urlParams.get('action');
        const scheduleId = urlParams.get('id');

        let apiUrl = '/shift-scheduler/api/shift-scheduler/save-daily-schedule';
        let method = 'POST';
        let successMessage = 'Schedule saved successfully!';

        // If editing existing schedule
        if (action === 'edit' && scheduleId) {
            apiUrl = `/shift-scheduler/api/shift-scheduler/update-daily-schedule/${scheduleId}`;
            method = 'PUT';
            successMessage = 'Schedule updated successfully!';
        }

        // Send to server
        $.ajax({
            url: apiUrl,
            method: method,
            contentType: 'application/json',
            data: JSON.stringify(requestData),
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showAlert(successMessage, 'success');

                    // Redirect after short delay
                    setTimeout(() => {
                        window.location.href = '/shift-scheduler/shift-scheduler';
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
                showAlert(`Invalid time range for ${day.dayName} (${day.date}): Start time must be before end time.`, 'warning');
                return false;
            }
            if (day.breakStart && day.breakEnd && day.breakStart >= day.breakEnd) {
                showAlert(`Invalid break time range for ${day.dayName} (${day.date}): Break start time must be before break end time.`, 'warning');
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

    // Event handlers for default time inputs and updates
    $(document).on('change', '#defaultStartTime, #defaultEndTime, #defaultBreakStart, #defaultBreakEnd', function() {
        updateDefaultTimeDisplays();
        updateDefaultBreakMinutes();
    });

    // Update time display and break minutes for row inputs
    $(document).on('change', '.time-input, .break-input', function() {
        const $input = $(this);
        const $row = $input.closest('tr');
        const index = parseInt($row.data('index'));
        const field = $input.data('field');
        const value = $input.val();

        if (currentScheduleDays[index]) {
            // Update the data array
            currentScheduleDays[index][field] = value;

            // Update the 12-hour display next to time inputs
            if (field === 'startTime' || field === 'endTime' || field === 'breakStart' || field === 'breakEnd') {
                updateTimeDisplay($input);
            }

            // Auto-calculate break minutes when break times change
            if (field === 'breakStart' || field === 'breakEnd') {
                const breakStart = currentScheduleDays[index].breakStart;
                const breakEnd = currentScheduleDays[index].breakEnd;
                const breakMinutes = calculateBreakMinutes(breakStart, breakEnd);
                currentScheduleDays[index].breakMinutes = breakMinutes;

                // Update the break minutes input
                $row.find('input[data-field="breakMinutes"]').val(breakMinutes);
            }

            updateReviewSection();
        }
    });

    /**
     * Load existing schedule data for view/edit mode
     */
    function loadExistingSchedule(action, scheduleId) {
        showLoadingModal('Loading schedule data...');

        $.ajax({
            url: `/shift-scheduler/api/schedule/${scheduleId}/details`,
            method: 'GET',
            success: function(response) {
                if (response.success) {
                    const schedule = response.schedule;

                    // Pre-fill basic information
                    $('#staffSelect').val(schedule.staff_id);
                    $('#scheduleName').val(schedule.schedule_name);
                    $('#fromDate').val(schedule.start_date);
                    $('#toDate').val(schedule.end_date);
                    $('#priority').val(schedule.priority);
                    $('#description').val(schedule.description);

                    // Update default time inputs from loaded schedule if they exist
                    if (schedule.shift_start_time) $('#defaultStartTime').val(schedule.shift_start_time);
                    if (schedule.shift_end_time) $('#defaultEndTime').val(schedule.shift_end_time);
                    // For breaks, we'll use defaults from the table if not explicitly loaded, as they are per day
                    // If backend provides default break times, they can be set here similarly.

                    // Update displays for default times
                    updateDefaultTimeDisplays();
                    updateDefaultBreakMinutes();


                    // Handle different modes
                    if (action === 'view') {
                        // Disable all day configuration inputs
                        $('#daysConfigTable input, #daysConfigTable select').prop('disabled', true);
                        $('#applyToAllBtn, #markWeekendsOffBtn, #applyDefaultsBtn').hide();
                        $('#saveScheduleBtn').hide();

                        // Change bulk config panel for view mode
                        $('#bulkConfigPanel').hide();
                    } else if (action === 'edit') {
                        // Update save button text for edit mode
                        $('#saveScheduleBtn').html('<i class="fas fa-save me-2"></i>Update Schedule');
                    }

                    // Auto-generate days for view/edit
                    generateDaysFromExisting(schedule);

                } else {
                    showAlert('Error loading schedule: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error loading schedule:', error);
                showAlert('Error loading schedule data. Please try again.', 'danger');
            }
        });
    }

    /**
     * Generate days table from existing schedule data
     */
    function generateDaysFromExisting(schedule) {
        const fromDate = schedule.start_date;
        const toDate = schedule.end_date;

        if (!fromDate || !toDate) {
            showAlert('Invalid date range in schedule', 'warning');
            return;
        }

        // Generate days array
        const days = [];
        let current = new Date(fromDate);
        const end = new Date(toDate);

        while (current <= end) {
            const dayOfWeek = current.getDay(); // 0 = Sunday, 6 = Saturday
            const dayName = current.toLocaleDateString('en-US', { weekday: 'long' });

            // Check if this day is a working day according to schedule
            const dayMapping = {
                0: 'sunday', 1: 'monday', 2: 'tuesday', 3: 'wednesday',
                4: 'thursday', 5: 'friday', 6: 'saturday'
            };
            const dayKey = dayMapping[dayOfWeek];
            // Schedule object might not have direct keys for days of week, assuming backend returns array `schedule_days`
            // If schedule has direct keys like schedule.monday, use that.
            // For now, let's assume schedule.schedule_days is an array of objects with date and working status.
            // This part needs adjustment based on the actual structure of the `schedule` object from the backend.

            // Placeholder for actual day-specific data from backend
            let dayData = {
                working: false,
                startTime: schedule.shift_start_time || '09:00',
                endTime: schedule.shift_end_time || '17:00',
                breakStart: '13:00', // Default break start
                breakEnd: '14:00',   // Default break end
                breakMinutes: 60,
                notes: ''
            };

            // If schedule object contains an array of schedule_days, loop through to find the entry for the current date
            if (schedule.schedule_days && Array.isArray(schedule.schedule_days)) {
                const matchingDay = schedule.schedule_days.find(d => d.date === formatDateForInput(current));
                if (matchingDay) {
                    dayData = {
                        working: matchingDay.working,
                        startTime: matchingDay.startTime,
                        endTime: matchingDay.endTime,
                        breakStart: matchingDay.breakStart,
                        breakEnd: matchingDay.breakEnd,
                        breakMinutes: matchingDay.breakMinutes,
                        notes: matchingDay.notes
                    };
                } else {
                    // If day not found in schedule_days, use general schedule times and default working status
                    dayData.working = (dayOfWeek !== 0 && dayOfWeek !== 6); // Default to weekday working if not specified
                }
            } else {
                // Fallback if schedule.schedule_days is not in expected format
                dayData.working = (dayOfWeek !== 0 && dayOfWeek !== 6); // Default to weekday working
            }


            days.push({
                date: formatDateForInput(current),
                dayName: dayName,
                dayOfWeek: dayOfWeek,
                working: dayData.working,
                startTime: dayData.startTime,
                endTime: dayData.endTime,
                breakStart: dayData.breakStart,
                breakEnd: dayData.breakEnd,
                breakMinutes: dayData.breakMinutes,
                notes: dayData.notes
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

        // Check URL action and disable inputs if view mode
        const urlParams = new URLSearchParams(window.location.search);
        const action = urlParams.get('action');

        if (action === 'view') {
            // Disable all day configuration inputs
            $('#daysConfigTable input, #daysConfigTable select').prop('disabled', true);
            $('#applyToAllBtn, #markWeekendsOffBtn, #applyDefaultsBtn').hide();
            $('#saveScheduleBtn').hide();

            // Change bulk config panel for view mode
            $('#bulkConfigPanel').hide();
        }
    }

    /**
     * Add minutes to a time string
     */
    function addMinutesToTime(timeString, minutes) {
        const [hours, mins] = timeString.split(':').map(Number);
        const totalMinutes = hours * 60 + mins + minutes;
        const newHours = Math.floor(totalMinutes / 60) % 24;
        const newMins = totalMinutes % 60;

        return `${String(newHours).padStart(2, '0')}:${String(newMins).padStart(2, '0')}`;
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

            return `${hour12.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')} ${ampm}`;
        } catch (error) {
            console.error('Time conversion error:', error);
            return time24;
        }
    }

    /**
     * Update the 12-hour display next to a time input
     */
    window.updateTimeDisplay = function(element) { // Make globally accessible for inline onchange
        const timeValue = $(element).val();
        if (timeValue) {
            const displayTime = convert24To12Hour(timeValue);
            $(element).siblings('.time-display').text(displayTime);
        }
    };

    /**
     * Update break time and calculate break minutes
     */
    window.updateBreakTime = function(element) { // Make globally accessible for inline onchange
        updateTimeDisplay(element); // Update the 12hr format display

        const $row = $(element).closest('tr');
        const index = parseInt($row.data('index'));
        const breakStart = $row.find('.break-start').val();
        const breakEnd = $row.find('.break-end').val();

        if (breakStart && breakEnd) {
            const breakMinutes = calculateBreakMinutes(breakStart, breakEnd);
            $row.find('.break-minutes').val(breakMinutes);

            // Update the data array
            if (currentScheduleDays[index]) {
                currentScheduleDays[index].breakStart = breakStart;
                currentScheduleDays[index].breakEnd = breakEnd;
                currentScheduleDays[index].breakMinutes = breakMinutes;
            }
        } else {
            // Clear break minutes if start or end is missing
            $row.find('.break-minutes').val('');
            if (currentScheduleDays[index]) {
                currentScheduleDays[index].breakStart = breakStart;
                currentScheduleDays[index].breakEnd = breakEnd;
                currentScheduleDays[index].breakMinutes = 0;
            }
        }
        updateReviewSection();
    };

    /**
     * Update out of office time and calculate minutes
     */
    window.updateOutOfOfficeTime = function(element) { // Make globally accessible for inline onchange
        updateTimeDisplay(element); // Update the 12hr format display

        const $row = $(element).closest('tr');
        const index = parseInt($row.data('index'));
        const outStart = $row.find('.out-start').val();
        const outEnd = $row.find('.out-end').val();

        if (outStart && outEnd) {
            const outMinutes = calculateBreakMinutes(outStart, outEnd);
            $row.find('.out-minutes').val(outMinutes);

            // Update the data array
            if (currentScheduleDays[index]) {
                currentScheduleDays[index].outOfOfficeStart = outStart;
                currentScheduleDays[index].outOfOfficeEnd = outEnd;
                currentScheduleDays[index].outOfOfficeMinutes = outMinutes;
            }
        } else {
            // Clear out of office minutes if start or end is missing
            $row.find('.out-minutes').val('');
            if (currentScheduleDays[index]) {
                currentScheduleDays[index].outOfOfficeStart = outStart;
                currentScheduleDays[index].outOfOfficeEnd = outEnd;
                currentScheduleDays[index].outOfOfficeMinutes = 0;
            }
        }
        updateReviewSection();
    };

    // Update summary when any input changes
    $(document).on('change input', '#daysConfigBody input, #daysConfigBody select', function() {
        updateReviewSection();
    });

    console.log('Add Shift Scheduler JavaScript fully loaded');

})();