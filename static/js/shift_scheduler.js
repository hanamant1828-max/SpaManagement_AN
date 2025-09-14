/**
 * Shift Scheduler JavaScript - New Inline Form Design
 * Implements Add, Edit, View, Delete operations with a single form
 */

(function() {
    'use strict';

    // Global variables
    let schedules = [];
    let currentMode = 'add';
    let editIndex = null;

    // Initialize when document is ready
    $(document).ready(function() {
        console.log('Shift Scheduler JavaScript loaded - New Design');
        initializeEventHandlers();
        loadSchedules();
        initializeUIEnhancements(); // Initialize UI enhancements
    });

    /**
     * Initialize all event handlers
     */
    function initializeEventHandlers() {
        // Add Shift button
        $('#addShiftBtn').on('click', function() {
            openForm('add');
        });

        // Cancel buttons
        $('#cancelFormBtn, #cancelBtn').on('click', function() {
            cancelForm();
        });

        // Form submission
        $('#shiftForm').on('submit', function(e) {
            e.preventDefault();
            handleFormSubmit();
        });

        // Office days selection change
        $('#officeDays').on('change', function() {
            const value = $(this).val();
            if (value === 'Custom') {
                $('#customDaysSection').show();
            } else {
                $('#customDaysSection').hide();
                setPresetDays(value);
            }
        });

        // Refresh button
        $('#refreshSchedulesBtn').on('click', function() {
            loadSchedules();
        });

        // Date validation
        $('#fromDate, #toDate').on('change', function() {
            validateDateRange();
        });

        // Enhanced table row interactions for schedules table
        $('#scheduleTable tbody').on('mouseenter', 'tr', function() {
            $(this).addClass('table-row-hover');
        }).on('mouseleave', 'tr', function() {
            $(this).removeClass('table-row-hover');
        });

        // Smooth scroll to sections
        $('a[href^="#"]').on('click', function(e) {
            e.preventDefault();
            const target = $($(this).attr('href'));
            if (target.length) {
                $('html, body').animate({
                    scrollTop: target.offset().top - 100
                }, 800, 'easeInOutCubic');
            }
        });

        // Loading state for buttons
        $('.btn').on('click', function() {
            const $btn = $(this);
            if (!$btn.hasClass('loading') && !$btn.hasClass('disabled')) {
                const originalHtml = $btn.html();
                $btn.addClass('loading disabled').html('<i class="fas fa-spinner fa-spin me-2"></i>Processing...');
                
                // Simulate async operation, then revert button state
                setTimeout(() => {
                    $btn.removeClass('loading disabled').html(originalHtml);
                }, 2000);
            }
        });

        // Progressive form validation feedback
        $('.form-control, .form-select').on('input change', function() {
            const $input = $(this);
            const $group = $input.closest('.form-group, .mb-3, .col-md-3, .col-md-4, .col-md-6');
            
            if (this.checkValidity()) {
                $group.removeClass('has-error').addClass('has-success');
                $input.removeClass('is-invalid').addClass('is-valid');
            } else {
                $group.removeClass('has-success').addClass('has-error');
                $input.removeClass('is-valid').addClass('is-invalid');
            }
        });

        // Tooltip initialization for action buttons
        $('[title]').tooltip({
            placement: 'top',
            trigger: 'hover'
        });

        // Add pulse animation to important buttons
        $('.btn-primary, .btn-success').addClass('pulse-animation');
    }

    /**
     * Open form in different modes (add, edit, view)
     */
    function openForm(mode, index = null) {
        currentMode = mode;
        editIndex = index;

        const formSection = $('#shiftFormSection');
        const formTitle = $('#formTitleText');
        const formIcon = $('#formIcon');
        const formHeader = $('#formHeader');
        const saveBtn = $('#saveBtn');
        const formActions = $('#formActions');

        // Reset form
        document.getElementById('shiftForm').reset();
        $('#formMode').val(mode);
        $('#editIndex').val(index || '');

        // Configure form based on mode
        switch(mode) {
            case 'add':
                formTitle.text('Add Shift');
                formIcon.removeClass('fa-edit fa-eye').addClass('fa-plus');
                formHeader.removeClass('bg-warning bg-info').addClass('bg-primary');
                saveBtn.html('<i class="fas fa-save me-2"></i>Save');
                enableFormFields(true);
                formActions.show();
                setDefaultValues();
                break;

            case 'edit':
                formTitle.text('Edit Shift');
                formIcon.removeClass('fa-plus fa-eye').addClass('fa-edit');
                formHeader.removeClass('bg-primary bg-info').addClass('bg-warning');
                saveBtn.html('<i class="fas fa-edit me-2"></i>Update');
                enableFormFields(true);
                formActions.show();
                fillForm(schedules[index]);
                break;

            case 'view':
                formTitle.text('View Shift');
                formIcon.removeClass('fa-plus fa-edit').addClass('fa-eye');
                formHeader.removeClass('bg-primary bg-warning').addClass('bg-info');
                enableFormFields(false);
                formActions.hide();
                fillForm(schedules[index]);
                break;
        }

        // Show form with animation
        formSection.slideDown(300);

        // Scroll to form
        $('html, body').animate({
            scrollTop: formSection.offset().top - 100
        }, 500);
    }

    /**
     * Enable or disable form fields
     */
    function enableFormFields(enable) {
        $('#shiftForm input, #shiftForm select, #shiftForm textarea').prop('disabled', !enable);
    }

    /**
     * Set default values for new form
     */
    function setDefaultValues() {
        const today = new Date();
        const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);

        $('#fromDate').val(today.toISOString().split('T')[0]);
        $('#toDate').val(nextWeek.toISOString().split('T')[0]);
        $('#startTime').val('09:00');
        $('#endTime').val('17:00');
        $('#breakTime').val('1 hour lunch');
        $('#priority').val('1');
        $('#officeDays').val('Mon-Fri');
        $('#officeDays').trigger('change'); // Trigger change to handle default selection
    }

    /**
     * Fill form with existing schedule data
     */
    function fillForm(schedule) {
        if (!schedule) return;

        $('#staffSelect').val(schedule.staff_id || schedule.staff);
        $('#fromDate').val(schedule.from_date || schedule.from);
        $('#toDate').val(schedule.to_date || schedule.to);
        $('#startTime').val(schedule.start_time || schedule.start);
        $('#endTime').val(schedule.end_time || schedule.end);
        $('#breakTime').val(schedule.break_time || schedule.break);
        $('#description').val(schedule.description || schedule.desc || '');
        $('#priority').val(schedule.priority || '1');

        // Set office days
        const officeDaysValue = schedule.office_days || getWorkingDaysFromSchedule(schedule);
        $('#officeDays').val(officeDaysValue);

        // Trigger office days change to show custom section if needed
        $('#officeDays').trigger('change');
    }

    /**
     * Get working days pattern from schedule
     */
    function getWorkingDaysFromSchedule(schedule) {
        const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
        const workingDays = days.filter(day => schedule[day] === true || schedule[day] === 1);

        // Check for common patterns
        if (workingDays.length === 7) return 'All';
        if (workingDays.length === 5 && !workingDays.includes('saturday') && !workingDays.includes('sunday')) return 'Mon-Fri';
        if (workingDays.length === 2 && workingDays.includes('saturday') && workingDays.includes('sunday')) return 'Weekends';

        return 'Custom';
    }

    /**
     * Set preset working days
     */
    function setPresetDays(preset) {
        // Clear all checkboxes first
        $('input[name="working_days"]').prop('checked', false);

        switch(preset) {
            case 'Mon-Fri':
                $('#monday, #tuesday, #wednesday, #thursday, #friday').prop('checked', true);
                break;
            case 'All':
                $('input[name="working_days"]').prop('checked', true);
                break;
            case 'Weekends':
                $('#saturday, #sunday').prop('checked', true);
                break;
        }
    }

    /**
     * Validate date range
     */
    function validateDateRange() {
        const fromDate = $('#fromDate').val();
        const toDate = $('#toDate').val();

        if (fromDate && toDate && new Date(fromDate) > new Date(toDate)) {
            showAlert('From date cannot be after to date', 'warning');
            $('#toDate').addClass('is-invalid');
            return false;
        } else {
            $('#toDate').removeClass('is-invalid');
            return true;
        }
    }

    /**
     * Handle form submission
     */
    function handleFormSubmit() {
        if (!validateForm()) return;

        const formData = collectFormData();

        if (currentMode === 'add') {
            saveSchedule(formData);
        } else if (currentMode === 'edit') {
            updateSchedule(formData, editIndex);
        }
    }

    /**
     * Validate form data
     */
    function validateForm() {
        const staffSelect = $('#staffSelect').val();
        const fromDate = $('#fromDate').val();
        const toDate = $('#toDate').val();
        const officeDays = $('#officeDays').val();
        const startTime = $('#startTime').val();
        const endTime = $('#endTime').val();

        if (!staffSelect) {
            showAlert('Please select a staff member', 'warning');
            return false;
        }

        if (!validateDateRange()) return false; // Use the dedicated date range validator

        if (!officeDays) {
            showAlert('Please select office days', 'warning');
            return false;
        }

        if (!startTime || !endTime) {
            showAlert('Please select both start and end times', 'warning');
            return false;
        }

        if (startTime >= endTime) {
            showAlert('End time must be after start time', 'warning');
            return false;
        }

        // Validate custom days if selected
        if (officeDays === 'Custom') {
            const checkedDays = $('input[name="working_days"]:checked').length;
            if (checkedDays === 0) {
                showAlert('Please select at least one working day', 'warning');
                return false;
            }
        }

        return true;
    }

    /**
     * Collect form data
     */
    function collectFormData() {
        const formData = {
            staff_id: parseInt($('#staffSelect').val()),
            staff_name: $('#staffSelect option:selected').text(),
            from_date: $('#fromDate').val(),
            to_date: $('#toDate').val(),
            office_days: $('#officeDays').val(),
            start_time: $('#startTime').val(),
            end_time: $('#endTime').val(),
            break_time: $('#breakTime').val(),
            description: $('#description').val(),
            priority: parseInt($('#priority').val())
        };

        // Add working days
        if (formData.office_days === 'Custom') {
            const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
            days.forEach(day => {
                formData[day] = $(`#${day}`).is(':checked');
            });
        } else {
            // Set working days based on preset
            const workingDays = getWorkingDaysFromPreset(formData.office_days);
            workingDays.forEach(day => {
                formData[day] = true;
            });
        }

        return formData;
    }

    /**
     * Get working days array from preset
     */
    function getWorkingDaysFromPreset(preset) {
        switch(preset) {
            case 'Mon-Fri':
                return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
            case 'All':
                return ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
            case 'Weekends':
                return ['saturday', 'sunday'];
            default:
                return [];
        }
    }

    /**
     * Save new schedule
     */
    function saveSchedule(formData) {
        showLoadingModal('Saving schedule...');

        $.ajax({
            url: '/shift-scheduler/save',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                staff_id: formData.staff_id,
                schedule_data: [formData]
            }),
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showAlert('Schedule saved successfully!', 'success');
                    cancelForm();
                    loadSchedules();
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
     * Update existing schedule
     */
    function updateSchedule(formData, index) {
        const schedule = schedules[index];
        if (!schedule || !schedule.id) {
            showAlert('Schedule not found for update', 'danger');
            return;
        }

        showLoadingModal('Updating schedule...');

        // Construct the data payload, potentially including date range changes
        const payload = {
            ...formData,
            // Add logic here if the API needs to know about date range changes explicitly
            // For now, assume the API handles it based on received dates
        };

        $.ajax({
            url: `/api/schedule/${schedule.id}/update-with-range`, // Using the more robust update endpoint
            method: 'PUT',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showAlert('Schedule updated successfully!', 'success');
                    cancelForm();
                    loadSchedules();
                } else {
                    showAlert('Error updating schedule: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error updating schedule:', error);
                showAlert('Error updating schedule. Please try again.', 'danger');
            }
        });
    }

    /**
     * Delete schedule
     */
    function deleteSchedule(index) {
        const schedule = schedules[index];
        if (!schedule || !schedule.id) {
            showAlert('Schedule not found for deletion', 'danger');
            return;
        }

        if (!confirm('Are you sure you want to delete this schedule? This action cannot be undone.')) {
            return;
        }

        showLoadingModal('Deleting schedule...');

        $.ajax({
            url: `/api/schedule/${schedule.id}`,
            method: 'DELETE',
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    showAlert('Schedule deleted successfully!', 'success');
                    loadSchedules();
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
     * Cancel form and hide
     */
    function cancelForm() {
        $('#shiftFormSection').slideUp(300);
        document.getElementById('shiftForm').reset();
        currentMode = 'add';
        editIndex = null;
        // Reset form validation states
        $('#shiftForm').find('.is-valid, .is-invalid').removeClass('is-valid is-invalid');
        $('#shiftForm').find('.has-error, .has-success').removeClass('has-error has-success');
    }

    /**
     * Load schedules from server
     */
    function loadSchedules() {
        showLoadingModal('Loading schedules...');

        $.ajax({
            url: '/api/all-schedules',
            method: 'GET',
            success: function(response) {
                hideLoadingModal();
                if (response.success) {
                    schedules = response.schedules || [];
                    renderScheduleTable();
                } else {
                    showAlert('Error loading schedules: ' + response.error, 'danger');
                }
            },
            error: function(xhr, status, error) {
                hideLoadingModal();
                console.error('Error loading schedules:', error);
                showAlert('Error loading schedules. Please try again.', 'danger');
            }
        });
    }

    /**
     * Render schedule table
     */
    function renderScheduleTable() {
        const tbody = $('#scheduleTableBody');
        tbody.empty();

        if (schedules.length === 0) {
            $('#scheduleTable').hide();
            $('#noSchedules').show();
            $('#scheduleCount').text('0');
            return;
        }

        $('#scheduleTable').show();
        $('#noSchedules').hide();
        $('#scheduleCount').text(schedules.length);

        schedules.forEach((schedule, index) => {
            const workingDaysText = formatWorkingDays(schedule);
            const timeText = `${schedule.shift_start_time || '09:00'} - ${schedule.shift_end_time || '17:00'}`;

            const row = `
                <tr class="schedule-management-row">
                    <td class="text-center">
                        <strong>${index + 1}</strong>
                    </td>
                    <td>
                        <div class="staff-info">
                            <strong class="text-primary">${schedule.staff_name || 'Unknown Staff'}</strong>
                            <br><small class="text-muted">${schedule.description || 'No description'}</small>
                        </div>
                    </td>
                    <td>
                        <span class="date-display">${formatDate(schedule.start_date)}</span>
                    </td>
                    <td>
                        <span class="date-display">${formatDate(schedule.end_date)}</span>
                    </td>
                    <td>
                        <span class="office-days-badge">${workingDaysText}</span>
                    </td>
                    <td>
                        <span class="badge bg-success">${timeText}</span>
                        ${schedule.break_time ? `<br><small class="text-muted">${schedule.break_time}</small>` : ''}
                    </td>
                    <td>
                        <div class="action-buttons-group">
                            <button type="button" class="btn btn-sm btn-outline-info me-1" 
                                    onclick="openForm('view', ${index})" 
                                    title="View Schedule">
                                <i class="fas fa-eye me-1"></i>View
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-warning me-1" 
                                    onclick="openForm('edit', ${index})" 
                                    title="Edit Schedule">
                                <i class="fas fa-edit me-1"></i>Edit
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-danger" 
                                    onclick="deleteSchedule(${index})" 
                                    title="Delete Schedule">
                                <i class="fas fa-trash me-1"></i>Delete
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });
    }

    /**
     * Format working days for display
     */
    function formatWorkingDays(schedule) {
        // Check if schedule.working_days is an array first
        if (schedule.working_days && Array.isArray(schedule.working_days)) {
            // If it's already an array of strings like "Mon", "Tue"
            return schedule.working_days.join(', ');
        }

        const days = [];
        const dayMap = {
            monday: 'Mon',
            tuesday: 'Tue',
            wednesday: 'Wed',
            thursday: 'Thu',
            friday: 'Fri',
            saturday: 'Sat',
            sunday: 'Sun'
        };

        Object.keys(dayMap).forEach(day => {
            // Check for boolean or numeric true/1
            if (schedule[day] === true || schedule[day] === 1) {
                days.push(dayMap[day]);
            }
        });

        if (days.length === 0) return 'No working days';
        if (days.length === 7) return 'All Days';
        if (days.length === 5 && !days.includes('Sat') && !days.includes('Sun')) return 'Mon to Fri';
        if (days.length === 2 && days.includes('Sat') && days.includes('Sun')) return 'Weekends';

        return days.join(', ');
    }

    /**
     * Format date for display
     */
    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            // Check if the date is valid
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
            <div class="alert ${alertClass} alert-dismissible fade show slide-in" role="alert" style="margin: 1rem 0;">
                <div class="d-flex align-items-center">
                    <i class="fas ${iconClass} me-3" style="font-size: 1.2em;"></i>
                    <div class="flex-grow-1">${message}</div>
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            </div>
        `;

        $('.container-fluid').prepend(alertHtml);

        setTimeout(() => {
            $('.alert').first().fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    }

    /**
     * Initialize UI enhancements
     */
    function initializeUIEnhancements() {
        // Add smooth fade-in animations to cards
        $('.card').each(function(index) {
            $(this).css('animation-delay', (index * 0.1) + 's');
            $(this).addClass('fade-in');
        });
        
        // Smooth form transitions
        $('.form-control, .form-select').on('focus', function() {
            $(this).parent().addClass('focused');
        }).on('blur', function() {
            $(this).parent().removeClass('focused');
        });
        
        // Smooth modal transitions
        $('.modal').on('show.bs.modal', function() {
            $(this).find('.modal-content').addClass('fade-in');
        });
        
        // Enhanced inline form animations
        $('#shiftFormSection').on('show', function() {
            $(this).addClass('slide-in');
        });
        
        // Auto-hide success alerts after 5 seconds
        $('.alert-success').delay(5000).fadeOut('slow');
        
        // Remove animations after they complete to improve performance
        setTimeout(() => {
            $('.fade-in, .slide-in').removeClass('fade-in slide-in');
        }, 1000);

        // Add smooth scrolling to top button
        const scrollToTopBtn = $('<button class="btn btn-primary position-fixed" id="scrollToTop" style="bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;"><i class="fas fa-arrow-up"></i></button>');
        $('body').append(scrollToTopBtn);
        
        $(window).scroll(function() {
            if ($(this).scrollTop() > 300) {
                $('#scrollToTop').fadeIn();
            } else {
                $('#scrollToTop').fadeOut();
            }
        });
        
        $('#scrollToTop').click(function() {
            $('html, body').animate({scrollTop: 0}, 800);
        });
    }

    // Make functions globally accessible
    window.openForm = openForm;
    window.deleteSchedule = deleteSchedule;

    console.log('Shift Scheduler JavaScript fully loaded with inline form functionality');

})();