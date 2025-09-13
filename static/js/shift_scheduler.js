
/**
 * Staff Shift Scheduler JavaScript
 * Complete functionality for schedule management
 */

// Global variables
let currentStaffId = null;
let scheduleData = [];
let existingSchedules = [];

// Color mapping for days of the week
const dayColors = {
    'Monday': '#007bff',    // Blue
    'Tuesday': '#17a2b8',   // Cyan  
    'Wednesday': '#28a745', // Green
    'Thursday': '#fd7e14',  // Orange
    'Friday': '#dc3545',    // Red
    'Saturday': '#6c757d',  // Gray
    'Sunday': '#6c757d'     // Gray
};

// Initialize when document is ready
$(document).ready(function() {
    console.log('Shift Scheduler JavaScript loaded');
    initializeEventHandlers();
    initializeDateInputs();
});

/**
 * Initialize all event handlers
 */
function initializeEventHandlers() {
    // Generate Days button
    $('#generateDaysBtn').on('click', function() {
        generateDays();
    });
    
    // Bulk action buttons
    $('#applyAllWorkingBtn').on('click', function() {
        applyToAll(true);
    });
    
    $('#setWeekendsOffBtn').on('click', function() {
        setWeekendsOff();
    });
    
    $('#clearAllBtn').on('click', function() {
        clearAll();
    });
    
    $('#applyDefaultTimesBtn').on('click', function() {
        applyDefaultTimes();
    });
    
    // Save and clear buttons
    $('#saveScheduleBtn').on('click', function() {
        saveSchedule();
    });
    
    $('#clearScheduleBtn').on('click', function() {
        if (confirm('Are you sure you want to clear all schedule data? This action cannot be undone.')) {
            clearScheduleTable();
        }
    });
    
    // Existing schedules refresh
    $('#refreshExistingBtn').on('click', function() {
        const staffId = $('#staffSelect').val();
        if (staffId) {
            loadExistingSchedules(staffId);
        }
    });
    
    // Delete selected schedules
    $('#deleteSelectedBtn').on('click', function() {
        deleteSelectedSchedules();
    });
    
    // Edit schedule form submission
    $('#editScheduleForm').on('submit', function(e) {
        e.preventDefault();
        updateSchedule();
    });
    
    // Staff selection change
    $('#staffSelect').on('change', function() {
        currentStaffId = $(this).val();
        if (currentStaffId) {
            loadExistingSchedules(currentStaffId);
            $('#selectedStaffName').text(' - ' + $(this).find('option:selected').data('name'));
        } else {
            clearExistingSchedules();
            $('#selectedStaffName').text('');
        }
    });
}

/**
 * Initialize date inputs with proper defaults
 */
function initializeDateInputs() {
    const today = new Date();
    const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    if (!$('#endDate').val()) {
        $('#endDate').val(nextWeek.toISOString().split('T')[0]);
    }
    
    // Initialize modal dates
    if (!$('#modalToDate').val()) {
        $('#modalToDate').val(nextWeek.toISOString().split('T')[0]);
    }
}

/**
 * Generate days based on selected date range
 */
function generateDays() {
    const staffId = $('#staffSelect').val();
    const startDate = $('#startDate').val();
    const endDate = $('#endDate').val();
    
    if (!staffId) {
        showAlert('Please select a staff member first', 'danger');
        return;
    }
    
    if (!startDate || !endDate) {
        showAlert('Please select both start and end dates', 'danger');
        return;
    }
    
    if (new Date(startDate) > new Date(endDate)) {
        showAlert('Start date cannot be after end date', 'danger');
        return;
    }
    
    // Clear previous data
    scheduleData = [];
    
    // Generate date range
    const start = new Date(startDate);
    const end = new Date(endDate);
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
        const dayName = days[date.getDay()];
        const formattedDate = date.toISOString().split('T')[0];
        
        scheduleData.push({
            date: formattedDate,
            day: dayName,
            working: true, // Default to working
            startTime: '09:00',
            endTime: '18:00',
            breakTime: '1 hour lunch',
            notes: ''
        });
    }
    
    // Load existing schedules for this date range
    loadExistingSchedulesForRange(staffId, startDate, endDate);
    
    // Render the schedule table
    renderScheduleTable();
    
    // Show the schedule controls
    $('#bulkActionsPanel').show();
    $('#scheduleTableCard').show();
    
    showAlert(`Generated ${scheduleData.length} days for scheduling`, 'success');
}

/**
 * Generate shift table for the modal
 */
function generateShiftTable() {
    console.log('generateShiftTable called');
    const staffId = $('#modalStaffSelect').val();
    const fromDate = $('#modalFromDate').val();
    const toDate = $('#modalToDate').val();
    
    if (!staffId) {
        showAlert('Please select a staff member first', 'danger');
        return;
    }
    
    if (!fromDate || !toDate) {
        showAlert('Please select both from and to dates', 'danger');
        return;
    }
    
    if (new Date(fromDate) > new Date(toDate)) {
        showAlert('From date cannot be after to date', 'danger');
        return;
    }
    
    const staffName = $('#modalStaffSelect option:selected').text();
    $('#shiftTableTitle').text(`Shift Schedule for ${staffName}`);
    
    // Generate date range
    const dates = [];
    const currentDate = new Date(fromDate);
    const endDate = new Date(toDate);
    
    while (currentDate <= endDate) {
        dates.push(new Date(currentDate));
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    // Generate table HTML
    let tableHtml = `
        <div class="table-responsive">
            <table class="table table-bordered">
                <thead class="table-primary">
                    <tr>
                        <th>Date</th>
                        <th>Day</th>
                        <th>Working</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Break Time</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    dates.forEach((date, index) => {
        const dateStr = date.toISOString().split('T')[0];
        const dayName = date.toLocaleDateString('en-US', { weekday: 'long' });
        const isWeekend = date.getDay() === 0 || date.getDay() === 6;
        
        tableHtml += `
            <tr data-date="${dateStr}">
                <td>${dateStr}</td>
                <td>${dayName}</td>
                <td>
                    <div class="form-check form-switch">
                        <input class="form-check-input working-toggle" type="checkbox" 
                               id="working_${index}" ${!isWeekend ? 'checked' : ''}>
                        <label class="form-check-label" for="working_${index}">
                            ${!isWeekend ? 'Yes' : 'No'}
                        </label>
                    </div>
                </td>
                <td>
                    <input type="time" class="form-control form-control-sm start-time" 
                           value="09:00" ${isWeekend ? 'disabled' : ''}>
                </td>
                <td>
                    <input type="time" class="form-control form-control-sm end-time" 
                           value="17:00" ${isWeekend ? 'disabled' : ''}>
                </td>
                <td>
                    <input type="text" class="form-control form-control-sm break-time" 
                           value="1 hour" ${isWeekend ? 'disabled' : ''}>
                </td>
                <td>
                    <input type="text" class="form-control form-control-sm notes" 
                           placeholder="Notes..." ${isWeekend ? 'disabled' : ''}>
                </td>
            </tr>
        `;
    });
    
    tableHtml += `
                </tbody>
            </table>
        </div>
        <div class="mt-3">
            <button type="button" class="btn btn-success" onclick="saveShiftSchedule()">
                <i class="fas fa-save me-2"></i>Save Schedule
            </button>
            <button type="button" class="btn btn-secondary ms-2" onclick="selectAllWorkingDays()">
                <i class="fas fa-check-double me-2"></i>All Working Days
            </button>
            <button type="button" class="btn btn-secondary ms-2" onclick="selectWeekendsOff()">
                <i class="fas fa-calendar-times me-2"></i>Weekends Off
            </button>
        </div>
    `;
    
    $('#shiftTableContainer').html(tableHtml);
    
    // Show the table section
    $('#shiftTableSection').show();
    
    // Add event listeners for working toggles
    $('.working-toggle').change(function() {
        const row = $(this).closest('tr');
        const timeInputs = row.find('.start-time, .end-time, .break-time, .notes');
        const label = $(this).next('label');
        
        if (this.checked) {
            timeInputs.prop('disabled', false);
            label.text('Yes');
            row.removeClass('table-secondary');
        } else {
            timeInputs.prop('disabled', true);
            label.text('No');
            row.addClass('table-secondary');
        }
    });
    
    showAlert(`Generated schedule table for ${staffName}`, 'success');
}

/**
 * Save shift schedule from modal
 */
function saveShiftSchedule() {
    console.log('saveShiftSchedule called');
    const staffId = $('#modalStaffSelect').val();
    
    if (!staffId) {
        showAlert('Please select a staff member', 'danger');
        return;
    }
    
    // Get all the schedule data from the modal table
    const modalScheduleData = [];
    $('#shiftTableContainer table tbody tr').each(function() {
        const row = $(this);
        const date = row.data('date');
        const isWorking = row.find('.working-toggle').is(':checked');
        const startTime = row.find('.start-time').val();
        const endTime = row.find('.end-time').val();
        const breakTime = row.find('.break-time').val();
        const notes = row.find('.notes').val();
        
        if (isWorking) {
            modalScheduleData.push({
                start_date: date,
                end_date: date,
                schedule_name: `${startTime} - ${endTime} Shift`,
                description: notes || '',
                shift_start_time: startTime,
                shift_end_time: endTime,
                break_time: breakTime || '',
                monday: new Date(date).getDay() === 1,
                tuesday: new Date(date).getDay() === 2,
                wednesday: new Date(date).getDay() === 3,
                thursday: new Date(date).getDay() === 4,
                friday: new Date(date).getDay() === 5,
                saturday: new Date(date).getDay() === 6,
                sunday: new Date(date).getDay() === 0,
                priority: 1
            });
        }
    });
    
    if (modalScheduleData.length === 0) {
        showAlert('No working days selected to save', 'warning');
        return;
    }
    
    showLoadingModal('Saving shift schedule...');
    
    $.ajax({
        url: '/shift-scheduler/save',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            staff_id: parseInt(staffId),
            schedule_data: modalScheduleData
        }),
        success: function(response) {
            hideLoadingModal();
            if (response.success) {
                showAlert(response.message, 'success');
                $('#addShiftModal').modal('hide');
                // Refresh existing schedules if staff is selected in main form
                const mainStaffId = $('#staffSelect').val();
                if (mainStaffId) {
                    loadExistingSchedules(mainStaffId);
                }
                // Clear the table
                $('#shiftTableSection').hide();
                $('#shiftTableContainer').empty();
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
 * Select all working days in modal
 */
function selectAllWorkingDays() {
    $('#shiftTableContainer table tbody tr').each(function() {
        const checkbox = $(this).find('.working-toggle');
        checkbox.prop('checked', true).trigger('change');
    });
    
    showAlert('Set all days as working days', 'success');
}

/**
 * Select weekends off in modal  
 */
function selectWeekendsOff() {
    $('#shiftTableContainer table tbody tr').each(function() {
        const row = $(this);
        const date = new Date(row.data('date'));
        const dayOfWeek = date.getDay(); // 0 = Sunday, 6 = Saturday
        
        const checkbox = row.find('.working-toggle');
        
        if (dayOfWeek === 0 || dayOfWeek === 6) {
            // Weekend - set as not working
            checkbox.prop('checked', false).trigger('change');
        } else {
            // Weekday - set as working
            checkbox.prop('checked', true).trigger('change');
        }
    });
    
    showAlert('Set weekends as off days', 'success');
}

/**
 * Load existing schedules for the selected date range
 */
function loadExistingSchedulesForRange(staffId, startDate, endDate) {
    $.ajax({
        url: '/api/shift-scheduler',
        method: 'GET',
        data: {
            staff_id: staffId,
            start_date: startDate,
            end_date: endDate
        },
        success: function(response) {
            if (response.success) {
                // Merge existing schedules with generated data
                response.schedules.forEach(function(existingSchedule) {
                    mergeExistingSchedule(existingSchedule);
                });
                
                // Re-render table with merged data
                renderScheduleTable();
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading existing schedules:', error);
        }
    });
}

/**
 * Merge existing schedule data with generated schedule data
 */
function mergeExistingSchedule(existingSchedule) {
    const scheduleStart = new Date(existingSchedule.start_date);
    const scheduleEnd = new Date(existingSchedule.end_date);
    const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    
    scheduleData.forEach(function(dayData) {
        const currentDate = new Date(dayData.date);
        
        // Check if current date falls within the existing schedule range
        if (currentDate >= scheduleStart && currentDate <= scheduleEnd) {
            const dayOfWeek = days[currentDate.getDay()];
            const isWorkingDay = existingSchedule[dayOfWeek];
            
            if (isWorkingDay !== undefined) {
                dayData.working = isWorkingDay;
                dayData.startTime = existingSchedule.shift_start_time || dayData.startTime;
                dayData.endTime = existingSchedule.shift_end_time || dayData.endTime;
                dayData.breakTime = existingSchedule.break_time || dayData.breakTime;
                dayData.notes = existingSchedule.description || dayData.notes;
            }
        }
    });
}

/**
 * Render the schedule table
 */
function renderScheduleTable() {
    const tbody = $('#scheduleTableBody');
    tbody.empty();
    
    scheduleData.forEach(function(dayData, index) {
        const row = createScheduleRow(dayData, index);
        tbody.append(row);
    });
}

/**
 * Create a schedule row
 */
function createScheduleRow(dayData, index) {
    const dayColor = dayColors[dayData.day] || '#6c757d';
    const isWeekend = dayData.day === 'Saturday' || dayData.day === 'Sunday';
    const workingClass = dayData.working ? 'table-success' : 'table-light';
    
    const row = $(`
        <tr class="${workingClass}" data-index="${index}">
            <td class="fw-bold">
                <i class="fas fa-calendar-day me-2" style="color: ${dayColor}"></i>
                ${formatDate(dayData.date)}
            </td>
            <td>
                <span class="badge text-white" style="background-color: ${dayColor};">
                    ${dayData.day}
                </span>
            </td>
            <td>
                <div class="form-check form-switch">
                    <input class="form-check-input working-toggle" type="checkbox" 
                           data-index="${index}" ${dayData.working ? 'checked' : ''}>
                    <label class="form-check-label">
                        ${dayData.working ? 'Working' : 'Off'}
                    </label>
                </div>
            </td>
            <td>
                <input type="time" class="form-control form-control-sm start-time" 
                       data-index="${index}" value="${dayData.startTime}" 
                       ${!dayData.working ? 'disabled' : ''}>
            </td>
            <td>
                <input type="time" class="form-control form-control-sm end-time" 
                       data-index="${index}" value="${dayData.endTime}" 
                       ${!dayData.working ? 'disabled' : ''}>
            </td>
            <td>
                <input type="text" class="form-control form-control-sm break-time" 
                       data-index="${index}" value="${dayData.breakTime}" 
                       placeholder="Break time" ${!dayData.working ? 'disabled' : ''}>
            </td>
            <td>
                <input type="text" class="form-control form-control-sm notes" 
                       data-index="${index}" value="${dayData.notes}" 
                       placeholder="Notes">
            </td>
        </tr>
    `);
    
    // Set up event handlers for this row
    setupRowEventHandlers(row, index);
    
    return row;
}

/**
 * Setup event handlers for a table row
 */
function setupRowEventHandlers(row, index) {
    // Working toggle
    row.find('.working-toggle').on('change', function() {
        const working = $(this).is(':checked');
        scheduleData[index].working = working;
        
        // Update UI
        const rowElement = $(this).closest('tr');
        rowElement.toggleClass('table-success', working);
        rowElement.toggleClass('table-light', !working);
        
        // Enable/disable time inputs
        const timeInputs = rowElement.find('.start-time, .end-time, .break-time');
        timeInputs.prop('disabled', !working);
        
        // Update label
        $(this).next('label').text(working ? 'Working' : 'Off');
    });
    
    // Time and note inputs
    row.find('.start-time').on('change', function() {
        scheduleData[index].startTime = $(this).val();
    });
    
    row.find('.end-time').on('change', function() {
        scheduleData[index].endTime = $(this).val();
    });
    
    row.find('.break-time').on('change', function() {
        scheduleData[index].breakTime = $(this).val();
    });
    
    row.find('.notes').on('change', function() {
        scheduleData[index].notes = $(this).val();
    });
}

/**
 * Apply working status to all days
 */
function applyToAll(working) {
    scheduleData.forEach(function(dayData) {
        dayData.working = working;
    });
    
    // Update UI
    $('.working-toggle').each(function() {
        $(this).prop('checked', working);
        $(this).trigger('change');
    });
    
    const message = working ? 'Set all days as working' : 'Set all days as off';
    showAlert(message, 'success');
}

/**
 * Set weekends as off
 */
function setWeekendsOff() {
    scheduleData.forEach(function(dayData, index) {
        if (dayData.day === 'Saturday' || dayData.day === 'Sunday') {
            dayData.working = false;
            
            // Update UI
            $(`.working-toggle[data-index="${index}"]`).prop('checked', false).trigger('change');
        }
    });
    
    showAlert('Weekend days set as off', 'success');
}

/**
 * Clear all schedule data
 */
function clearAll() {
    scheduleData.forEach(function(dayData, index) {
        dayData.working = false;
        dayData.startTime = '';
        dayData.endTime = '';
        dayData.breakTime = '';
        dayData.notes = '';
        
        // Update UI
        const rowElement = $(`tr[data-index="${index}"]`);
        rowElement.find('.working-toggle').prop('checked', false).trigger('change');
        rowElement.find('.start-time').val('');
        rowElement.find('.end-time').val('');
        rowElement.find('.break-time').val('');
        rowElement.find('.notes').val('');
    });
    
    showAlert('All schedule data cleared', 'info');
}

/**
 * Apply default times to all working days
 */
function applyDefaultTimes() {
    const defaultStart = $('#defaultStartTime').val();
    const defaultEnd = $('#defaultEndTime').val();
    
    if (!defaultStart || !defaultEnd) {
        showAlert('Please set both default start and end times', 'danger');
        return;
    }
    
    scheduleData.forEach(function(dayData, index) {
        if (dayData.working) {
            dayData.startTime = defaultStart;
            dayData.endTime = defaultEnd;
            
            // Update UI
            $(`.start-time[data-index="${index}"]`).val(defaultStart);
            $(`.end-time[data-index="${index}"]`).val(defaultEnd);
        }
    });
    
    showAlert('Default times applied to all working days', 'success');
}

/**
 * Save schedule to server
 */
function saveSchedule() {
    const staffId = $('#staffSelect').val();
    
    if (!staffId) {
        showAlert('Please select a staff member', 'danger');
        return;
    }
    
    if (!scheduleData.length) {
        showAlert('No schedule data to save. Please generate days first.', 'danger');
        return;
    }
    
    // Validate schedule data
    const validationErrors = validateScheduleData();
    if (validationErrors.length > 0) {
        showAlert('Validation errors: ' + validationErrors.join(', '), 'danger');
        return;
    }
    
    // Group consecutive working days into ranges
    const scheduleRanges = groupIntoRanges(scheduleData);
    
    showLoadingModal('Saving schedule...');
    
    $.ajax({
        url: '/shift-scheduler/save',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            staff_id: parseInt(staffId),
            schedule_data: scheduleRanges
        }),
        success: function(response) {
            hideLoadingModal();
            if (response.success) {
                showAlert(response.message, 'success');
                // Refresh existing schedules
                loadExistingSchedules(staffId);
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
 * Validate schedule data
 */
function validateScheduleData() {
    const errors = [];
    
    scheduleData.forEach(function(dayData, index) {
        if (dayData.working) {
            if (!dayData.startTime) {
                errors.push(`Row ${index + 1}: Start time is required for working days`);
            }
            if (!dayData.endTime) {
                errors.push(`Row ${index + 1}: End time is required for working days`);
            }
            if (dayData.startTime && dayData.endTime && dayData.startTime >= dayData.endTime) {
                errors.push(`Row ${index + 1}: End time must be after start time`);
            }
        }
    });
    
    return errors;
}

/**
 * Group schedule data into date ranges
 */
function groupIntoRanges(data) {
    const ranges = [];
    let currentRange = null;
    
    data.forEach(function(dayData) {
        // Start a new range if needed
        if (!currentRange || 
            !isSameSchedule(currentRange, dayData) || 
            !isConsecutiveDate(currentRange.end_date, dayData.date)) {
            
            // Save previous range
            if (currentRange) {
                ranges.push(currentRange);
            }
            
            // Start new range
            currentRange = {
                start_date: dayData.date,
                end_date: dayData.date,
                schedule_name: generateScheduleName(dayData),
                description: dayData.notes || '',
                shift_start_time: dayData.working ? dayData.startTime : null,
                shift_end_time: dayData.working ? dayData.endTime : null,
                break_time: dayData.working ? dayData.breakTime : '',
                monday: false,
                tuesday: false,
                wednesday: false,
                thursday: false,
                friday: false,
                saturday: false,
                sunday: false,
                priority: 1
            };
            
            // Set working day
            const dayName = dayData.day.toLowerCase();
            if (dayData.working) {
                currentRange[dayName] = true;
            }
        } else {
            // Extend current range
            currentRange.end_date = dayData.date;
            const dayName = dayData.day.toLowerCase();
            if (dayData.working) {
                currentRange[dayName] = true;
            }
        }
    });
    
    // Don't forget the last range
    if (currentRange) {
        ranges.push(currentRange);
    }
    
    return ranges;
}

/**
 * Check if two schedule items have the same working pattern
 */
function isSameSchedule(range, dayData) {
    return range.shift_start_time === (dayData.working ? dayData.startTime : null) &&
           range.shift_end_time === (dayData.working ? dayData.endTime : null) &&
           range.break_time === (dayData.working ? dayData.breakTime : '');
}

/**
 * Check if two dates are consecutive
 */
function isConsecutiveDate(date1, date2) {
    const d1 = new Date(date1);
    const d2 = new Date(date2);
    d1.setDate(d1.getDate() + 1);
    return d1.toISOString().split('T')[0] === d2;
}

/**
 * Generate a schedule name based on the working pattern
 */
function generateScheduleName(dayData) {
    if (!dayData.working) {
        return 'Off Day';
    }
    
    const startTime = dayData.startTime || '09:00';
    const endTime = dayData.endTime || '18:00';
    return `${startTime} - ${endTime} Shift`;
}

/**
 * Clear the schedule table
 */
function clearScheduleTable() {
    scheduleData = [];
    $('#scheduleTableBody').empty();
    $('#bulkActionsPanel').hide();
    $('#scheduleTableCard').hide();
}

/**
 * Load existing schedules for a staff member
 */
function loadExistingSchedules(staffId) {
    $.ajax({
        url: `/api/staff/${staffId}/all-schedules`,
        method: 'GET',
        success: function(response) {
            if (response.success) {
                existingSchedules = response.schedules;
                renderExistingSchedules();
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading existing schedules:', error);
            showAlert('Error loading existing schedules', 'danger');
        }
    });
}

/**
 * Render existing schedules list
 */
function renderExistingSchedules() {
    const container = $('#existingSchedulesContainer');
    
    if (!existingSchedules.length) {
        container.html(`
            <div class="text-center text-muted py-4" id="noExistingSchedules">
                <i class="fas fa-calendar-times fa-3x mb-3"></i>
                <p>No existing schedules found for this staff member.</p>
            </div>
        `);
        $('#existingSchedulesCount').text('0');
        return;
    }
    
    let html = '<div class="row g-3">';
    
    existingSchedules.forEach(function(schedule) {
        const workingDaysText = schedule.working_days.length > 0 ? 
            schedule.working_days.join(', ') : 'No working days';
        
        const timeText = schedule.shift_start_time && schedule.shift_end_time ?
            `${schedule.shift_start_time} - ${schedule.shift_end_time}` : 'No times set';
        
        html += `
            <div class="col-md-6 col-lg-4">
                <div class="card schedule-card h-100" data-schedule-id="${schedule.id}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">${schedule.schedule_name}</h6>
                            <div class="form-check">
                                <input class="form-check-input schedule-checkbox" type="checkbox" 
                                       value="${schedule.id}">
                            </div>
                        </div>
                        <p class="card-text small text-muted mb-2">
                            <i class="fas fa-calendar me-1"></i>
                            ${formatDate(schedule.start_date)} - ${formatDate(schedule.end_date)}
                        </p>
                        <p class="card-text small mb-2">
                            <i class="fas fa-clock me-1"></i>${timeText}
                        </p>
                        <p class="card-text small mb-3">
                            <i class="fas fa-calendar-days me-1"></i>${workingDaysText}
                        </p>
                        ${schedule.description ? `<p class="card-text small text-muted">${schedule.description}</p>` : ''}
                        <div class="d-flex justify-content-between">
                            <button type="button" class="btn btn-sm btn-outline-warning edit-schedule-btn" 
                                    data-schedule-id="${schedule.id}">
                                <i class="fas fa-edit me-1"></i>Edit
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger delete-schedule-btn" 
                                    data-schedule-id="${schedule.id}">
                                <i class="fas fa-trash me-1"></i>Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.html(html);
    $('#existingSchedulesCount').text(existingSchedules.length);
    
    // Setup event handlers for existing schedules
    setupExistingScheduleHandlers();
}

/**
 * Setup event handlers for existing schedule cards
 */
function setupExistingScheduleHandlers() {
    // Edit schedule buttons
    $('.edit-schedule-btn').on('click', function() {
        const scheduleId = $(this).data('schedule-id');
        openEditScheduleModal(scheduleId);
    });
    
    // Delete schedule buttons
    $('.delete-schedule-btn').on('click', function() {
        const scheduleId = $(this).data('schedule-id');
        deleteSchedule(scheduleId);
    });
    
    // Schedule checkboxes
    $('.schedule-checkbox').on('change', function() {
        const hasChecked = $('.schedule-checkbox:checked').length > 0;
        $('#deleteSelectedBtn').toggle(hasChecked);
    });
}

/**
 * Open edit schedule modal
 */
function openEditScheduleModal(scheduleId) {
    const schedule = existingSchedules.find(s => s.id == scheduleId);
    if (!schedule) return;
    
    // Populate form
    $('#editScheduleId').val(schedule.id);
    $('#editScheduleName').val(schedule.schedule_name);
    $('#editPriority').val(schedule.priority);
    $('#editStartDate').val(schedule.start_date);
    $('#editEndDate').val(schedule.end_date);
    $('#editShiftStart').val(schedule.shift_start_time);
    $('#editShiftEnd').val(schedule.shift_end_time);
    $('#editBreakTime').val(schedule.break_time);
    $('#editDescription').val(schedule.description);
    
    // Set working days checkboxes
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    days.forEach(day => {
        const checkbox = $(`#edit${day.charAt(0).toUpperCase() + day.slice(1)}`);
        checkbox.prop('checked', schedule.working_days.includes(day.substring(0, 3).charAt(0).toUpperCase() + day.substring(0, 3).slice(1)));
    });
    
    // Show modal
    $('#editScheduleModal').modal('show');
}

/**
 * Update schedule
 */
function updateSchedule() {
    const formData = new FormData($('#editScheduleForm')[0]);
    const scheduleId = formData.get('schedule_id');
    
    const data = {
        schedule_name: formData.get('schedule_name'),
        description: formData.get('description'),
        start_date: formData.get('start_date'),
        end_date: formData.get('end_date'),
        shift_start_time: formData.get('shift_start_time'),
        shift_end_time: formData.get('shift_end_time'),
        break_time: formData.get('break_time'),
        priority: parseInt(formData.get('priority')),
        monday: formData.has('monday'),
        tuesday: formData.has('tuesday'),
        wednesday: formData.has('wednesday'),
        thursday: formData.has('thursday'),
        friday: formData.has('friday'),
        saturday: formData.has('saturday'),
        sunday: formData.has('sunday')
    };
    
    $.ajax({
        url: `/api/schedule/${scheduleId}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            if (response.success) {
                showAlert('Schedule updated successfully', 'success');
                $('#editScheduleModal').modal('hide');
                loadExistingSchedules(currentStaffId);
            } else {
                showAlert('Error updating schedule: ' + response.error, 'danger');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error updating schedule:', error);
            showAlert('Error updating schedule. Please try again.', 'danger');
        }
    });
}

/**
 * Delete a single schedule
 */
function deleteSchedule(scheduleId) {
    if (!confirm('Are you sure you want to delete this schedule?')) {
        return;
    }
    
    $.ajax({
        url: `/api/schedule/${scheduleId}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                showAlert('Schedule deleted successfully', 'success');
                loadExistingSchedules(currentStaffId);
            } else {
                showAlert('Error deleting schedule: ' + response.error, 'danger');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error deleting schedule:', error);
            showAlert('Error deleting schedule. Please try again.', 'danger');
        }
    });
}

/**
 * Delete selected schedules
 */
function deleteSelectedSchedules() {
    const selectedIds = $('.schedule-checkbox:checked').map(function() {
        return $(this).val();
    }).get();
    
    if (!selectedIds.length) {
        showAlert('No schedules selected', 'warning');
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} schedule(s)?`)) {
        return;
    }
    
    $.ajax({
        url: '/shift-scheduler/delete',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            schedule_ids: selectedIds.map(id => parseInt(id))
        }),
        success: function(response) {
            if (response.success) {
                showAlert(`${response.deleted_count} schedule(s) deleted successfully`, 'success');
                loadExistingSchedules(currentStaffId);
                $('#deleteSelectedBtn').hide();
            } else {
                showAlert('Error deleting schedules: ' + response.error, 'danger');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error deleting schedules:', error);
            showAlert('Error deleting schedules. Please try again.', 'danger');
        }
    });
}

/**
 * Clear existing schedules display
 */
function clearExistingSchedules() {
    $('#existingSchedulesContainer').html(`
        <div class="text-center text-muted py-4" id="noExistingSchedules">
            <i class="fas fa-calendar-times fa-3x mb-3"></i>
            <p>No existing schedules found. Select a staff member to view their schedules.</p>
        </div>
    `);
    $('#existingSchedulesCount').text('0');
    $('#deleteSelectedBtn').hide();
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Show loading modal
 */
function showLoadingModal(message) {
    $('#loadingMessage').text(message);
    $('#loadingModal').modal('show');
}

/**
 * Hide loading modal
 */
function hideLoadingModal() {
    $('#loadingModal').modal('hide');
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
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${iconClass} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at top of container  
    $('.container-fluid').prepend(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        $('.alert').first().alert('close');
    }, 5000);
}

console.log('Shift Scheduler JavaScript fully loaded');
