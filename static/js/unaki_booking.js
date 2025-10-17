            // Cancel all appointments for a specific customer from Unaki booking view
            function cancelAllCustomerAppointments(customerId, customerName) {
                if (!customerId) {
                    alert('Please select a customer first');
                    return;
                }

                // Get all appointments for this customer
                fetch(`/api/unaki/customer-appointments/${customerId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success && data.bookings) {
                            const activeAppointments = data.bookings.filter(
                                apt => apt.status === 'scheduled' || apt.status === 'confirmed'
                            );

                            if (activeAppointments.length === 0) {
                                alert('No active appointments found for this customer');
                                return;
                            }

                            const appointmentsList = activeAppointments.map(apt =>
                                `- ${apt.service_name} on ${apt.appointment_date} at ${apt.start_time}`
                            ).join('\n');

                            const confirmMessage = `Are you sure you want to cancel ALL ${activeAppointments.length} appointment(s) for ${customerName}?\n\nAppointments:\n${appointmentsList}`;

                            if (confirm(confirmMessage)) {
                                // Cancel all appointments using PATCH endpoint
                                const cancelPromises = activeAppointments.map(apt =>
                                    fetch(`/api/unaki/bookings/${apt.id}`, {
                                        method: 'PATCH',
                                        headers: {
                                            'Content-Type': 'application/json',
                                        },
                                        body: JSON.stringify({ status: 'cancelled' })
                                    }).then(r => r.json())
                                );

                                Promise.all(cancelPromises)
                                    .then(results => {
                                        const successCount = results.filter(r => r.success).length;
                                        const failCount = results.length - successCount;

                                        if (failCount === 0) {
                                            alert(`✅ Successfully cancelled all ${successCount} appointments for ${customerName}`);
                                            // Refresh the schedule
                                            refreshSchedule();
                                        } else {
                                            alert(`⚠️ Cancelled ${successCount} appointments, ${failCount} failed`);
                                            refreshSchedule();
                                        }
                                    })
                                    .catch(error => {
                                        console.error('Error cancelling appointments:', error);
                                        alert('Error cancelling appointments. Please try again.');
                                    });
                            }
                        } else {
                            alert('Failed to load customer appointments');
                        }
                    })
                    .catch(error => {
                        console.error('Error loading appointments:', error);
                        alert('Error loading customer appointments');
                    });
            }

// ========== Second Script Block ==========

            // ==========================================
            // GLOBAL VARIABLES & STATE
            // ==========================================
            let selectedAppointmentId = null;
            const currentDate = window.UNAKI_CONFIG.today;
            let bookingsData = [];
            let appointmentCounter = 1;

            // ==========================================
            // TIME FORMAT CONVERSION - 12-HOUR AM/PM ONLY
            // ==========================================

            // Convert 24-hour time to 12-hour AM/PM format
            function convertTo12Hour(time24) {
                if (!time24) return '';

                const [hours, minutes] = time24.split(':');
                let hour = parseInt(hours);
                const ampm = hour >= 12 ? 'PM' : 'AM';

                hour = hour % 12 || 12;

                return `${hour}:${minutes} ${ampm}`;
            }

            // Convert 12-hour AM/PM time to 24-hour format
            function convertTo24Hour(time12, ampm) {
                let [hours, minutes] = time12.split(':');
                hours = parseInt(hours);

                if (ampm === 'PM' && hours !== 12) {
                    hours += 12;
                } else if (ampm === 'AM' && hours === 12) {
                    hours = 0;
                }

                return `${hours.toString().padStart(2, '0')}:${minutes}`;
            }

            // Validate time input (HH:MM format with proper ranges)
            function validateTimeInput(timeStr, ampm) {
                // Regex: H:MM or HH:MM format
                const timeRegex = /^([0-9]|0[0-9]|1[0-2]):([0-5][0-9])$/;

                if (!timeRegex.test(timeStr)) {
                    return { valid: false, error: 'Invalid time format. Use HH:MM (e.g., 2:30)' };
                }

                const [hours, minutes] = timeStr.split(':').map(Number);

                // Validate hours (1-12 for 12-hour format)
                if (hours < 1 || hours > 12) {
                    return { valid: false, error: 'Hours must be between 1 and 12' };
                }

                // Validate minutes (0-59)
                if (minutes < 0 || minutes > 59) {
                    return { valid: false, error: 'Minutes must be between 0 and 59' };
                }

                // Validate AM/PM
                if (ampm !== 'AM' && ampm !== 'PM') {
                    return { valid: false, error: 'Please specify AM or PM' };
                }

                return { valid: true };
            }

            // Populate time dropdown with 15-minute intervals
            function populateTimeOptions(selectElement, startHour = 9, endHour = 21, selectedTime = '09:00') {
                selectElement.innerHTML = '';

                for (let hour = startHour; hour <= endHour; hour++) {
                    for (let minute = 0; minute < 60; minute += 15) {
                        const time24 = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                        const time12 = convertTo12Hour(time24);
                        const option = document.createElement('option');
                        option.value = time24;
                        option.textContent = time12;
                        if (time24 === selectedTime) {
                            option.selected = true;
                        }
                        selectElement.appendChild(option);
                    }
                }
            }


            // ==========================================
            // INITIALIZATION
            // ==========================================
            document.addEventListener("DOMContentLoaded", function() {
                initializeApp();
                setupEventListeners();
                setupTooltips();
                setupScrollSync();
                initializeSearchableDropdowns();
            });

            function initializeApp() {
                loadBookings();
                loadShiftSchedule();
                updateCurrentTimeLine();
                setInterval(updateCurrentTimeLine, 60000);

                // Close context menu on click outside
                document.addEventListener("click", hideContextMenu);

                // Keyboard shortcuts
                document.addEventListener("keydown", function(e) {
                    if (e.key === "r" && (e.ctrlKey || e.metaKey)) {
                        e.preventDefault();
                        refreshSchedule();
                    }
                });

                // Initialize context menu
                setTimeout(() => {
                    if (window.appointmentContextMenu?.reinitializeForAppointments) {
                        window.appointmentContextMenu.reinitializeForAppointments();
                    }
                }, 100);
            }

            // ==========================================
            // EVENT LISTENERS
            // ==========================================
            function setupEventListeners() {
                // Handle Quick Add Client modal z-index on show
                const quickAddModal = document.getElementById('quickAddClientModal');
                if (quickAddModal) {
                    quickAddModal.addEventListener('show.bs.modal', function() {
                        this.style.zIndex = '1065';
                        setTimeout(() => {
                            const backdrops = document.querySelectorAll('.modal-backdrop');
                            if (backdrops.length > 0) {
                                backdrops[backdrops.length - 1].style.zIndex = '1060';
                            }
                        }, 50);
                    });

                }

                // Edit modal changes
                const editServiceSelect = document.getElementById('editServiceSelect');
                const editStartTime = document.getElementById('editStartTime');
                if (editServiceSelect) {
                    editServiceSelect.addEventListener('change', function() {
                        const serviceOption = this.selectedOptions[0];
                        const duration = parseInt(serviceOption?.dataset.duration || 0);
                        const startTime = document.getElementById('editStartTime').value;
                        if (startTime && duration) {
                            const endTime = calculateEndTimeFromDuration(startTime, duration);
                            document.getElementById('editEndTime').value = endTime;
                        }
                    });
                }
                if (editStartTime) {
                    editStartTime.addEventListener('change', function() {
                        const serviceSelect = document.getElementById('editServiceSelect');
                        const serviceOption = serviceSelect?.selectedOptions[0];
                        const duration = parseInt(serviceOption?.dataset.duration || 0);
                        if (this.value && duration) {
                            const endTime = calculateEndTimeFromDuration(this.value, duration);
                            document.getElementById('editEndTime').value = endTime;
                        }
                    });
                }
            }

            function setupTooltips() {
                const tooltip = document.getElementById("tooltip");
                document.querySelectorAll("[data-tooltip]").forEach(element => {
                    element.addEventListener("mouseenter", function(e) {
                        tooltip.textContent = this.getAttribute("data-tooltip");
                        tooltip.classList.add("show");
                        const rect = this.getBoundingClientRect();
                        tooltip.style.left = rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px";
                        tooltip.style.top = rect.bottom + 8 + "px";
                    });
                    element.addEventListener("mouseleave", () => tooltip.classList.remove("show"));
                });
            }

            function setupScrollSync() {
                const panel = document.querySelector(".timeline-panel");
                const staff = document.querySelector(".staff-sidebar");
                const headerInner = document.getElementById("timelineHeaderInner");

                if (!panel || !staff || !headerInner) return;

                let syncingFromPanel = false;
                let syncingFromStaff = false;

                panel.addEventListener("scroll", () => {
                    if (!syncingFromStaff) {
                        syncingFromPanel = true;
                        staff.scrollTop = panel.scrollTop;
                    }
                    syncingFromStaff = false;
                    headerInner.style.transform = `translateX(-${panel.scrollLeft}px)`;
                }, { passive: true });

                staff.addEventListener("scroll", () => {
                    if (!syncingFromPanel) {
                        syncingFromStaff = true;
                        panel.scrollTop = staff.scrollTop;
                    }
                    syncingFromPanel = false;
                }, { passive: true });
            }

            function initializeSearchableDropdowns() {
                if (typeof $.fn.select2 !== 'undefined') {
                    // Destroy existing Select2 instances first
                    $('.select2-dropdown.select2-hidden-accessible').select2('destroy');

                    // Initialize select2 for regular dropdowns (excluding check-in dropdown)
                    $('.select2-dropdown').not('#checkinClientSelect').select2({
                        width: '100%',
                        placeholder: function() {
                            return $(this).find('option:first').text();
                        },
                        allowClear: true
                    });

                    // Check-in client dropdown uses normal select (no Select2)
                    const checkinSelect = document.getElementById('checkinClientSelect');
                    if (checkinSelect && checkinSelect.options.length <= 1) {
                        console.log('⚠️ Check-in client dropdown has no clients loaded');
                        // Try to reload clients via API
                        fetch('/api/customers')
                            .then(response => response.json())
                            .then(customers => {
                                checkinSelect.innerHTML = '<option value="">Choose a client...</option>';
                                customers.forEach(customer => {
                                    const option = document.createElement('option');
                                    option.value = customer.id;
                                    option.textContent = `${customer.name} - ${customer.phone}`;
                                    checkinSelect.appendChild(option);
                                });
                                console.log(`✅ Loaded ${customers.length} clients into check-in dropdown`);
                            })
                            .catch(error => {
                                console.error('Error loading clients:', error);
                            });
                    }
                }
            }
            // ==========================================
            // DATA LOADING
            // ==========================================
            function loadBookings() {
                showLoading(true);
                fetch("/api/unaki/get-bookings?date=" + currentDate)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Filter out cancelled appointments
                            bookingsData = (data.bookings || []).filter(b => b.status !== "cancelled");
                            renderBookings();
                            updateStats();
                        } else {
                            showNotification("Failed to load bookings: " + data.error, "error");
                        }
                    })
                    .catch(error => {
                        console.error("Error loading bookings:", error);
                        showNotification("An error occurred while loading bookings.", "error");
                    })
                    .finally(() => showLoading(false));
            }

            function loadShiftSchedule() {
                fetch("/api/unaki/schedule?date=" + currentDate)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            renderShiftOverlays(data.staff);
                        }
                    })
                    .catch(error => console.error('Error loading shift schedule:', error));
            }

            function loadCustomerExistingAppointments(customerId) {
                const container = document.getElementById('customerExistingAppointments');
                const listDiv = document.getElementById('customerAppointmentsList');
                const countBadge = document.getElementById('customerAppointmentsCount');

                if (!customerId) {
                    container.style.display = 'none';
                    return;
                }

                container.style.display = 'block';
                listDiv.innerHTML = '<small class="text-muted"><i class="fas fa-spinner fa-spin me-1"></i>Loading...</small>';

                fetch(`/api/unaki/customer-appointments/${customerId}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success && data.bookings?.length > 0) {
                            countBadge.textContent = data.bookings.length;
                            displayCustomerAppointments(data.bookings);
                        } else {
                            countBadge.textContent = '0';
                            listDiv.innerHTML = '<small class="text-muted"><i class="fas fa-info-circle me-1"></i>No upcoming appointments</small>';
                        }
                    })
                    .catch(err => {
                        console.error('Error loading customer appointments:', err);
                        listDiv.innerHTML = '<small class="text-danger"><i class="fas fa-exclamation-triangle me-1"></i>Error loading appointments</small>';
                    });
            }

            function displayCustomerAppointments(appointments) {
                const listDiv = document.getElementById('customerAppointmentsList');
                let html = '<div class="list-group list-group-flush">';

                appointments.forEach(apt => {
                    const date = new Date(apt.appointment_date);
                    const formattedDate = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
                    const statusColor = apt.status === 'confirmed' ? 'success' : apt.status === 'scheduled' ? 'primary' : 'secondary';

                    html += `
                        <div class="list-group-item px-2 py-2" style="border: none; border-bottom: 1px solid #eee;">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <div class="fw-semibold" style="font-size: 0.9rem;">
                                        <i class="fas fa-spa me-1" style="color: var(--primary-color);"></i>${apt.service_names || apt.service_name || 'Service'}
                                    </div>
                                    <small class="text-muted">
                                        <i class="fas fa-calendar me-1"></i>${formattedDate}
                                        <i class="fas fa-clock ms-2 me-1"></i>${apt.start_time} - ${apt.end_time}
                                    </small>
                                    <br>
                                    <small class="text-muted"><i class="fas fa-user-nurse me-1"></i>${apt.staff_name}</small>
                                </div>
                                <span class="badge bg-${statusColor}" style="font-size: 0.7rem;">${apt.status}</span>
                            </div>
                        </div>
                    `;
                });

                html += '</div>';
                listDiv.innerHTML = html;
            }

            // ==========================================
            // RENDERING
            // ==========================================
            function renderBookings() {
                console.log('📋 Rendering bookings:', bookingsData.length);

                // Clear existing appointments
                document.querySelectorAll('.appointment-block').forEach(block => block.remove());

                // Show all bookings (including paid ones)
                const visibleBookings = bookingsData;
                console.log(`📊 Rendering ${visibleBookings.length} bookings`);

                // Render each booking
                visibleBookings.forEach(booking => {
                    const row = document.querySelector(`.timeline-row[data-staff-id="${booking.staff_id}"]`);
                    if (!row) return;

                    const startHour = parseFloat(booking.start_hour);
                    const startMinute = parseFloat(booking.start_minute);
                    const hoursSince9AM = startHour - 9 + startMinute / 60;
                    const leftPosition = hoursSince9AM * 140;

                    // Calculate actual duration from start_time and end_time
                    let durationMinutes = booking.duration; // Default fallback
                    if (booking.start_time && booking.end_time) {
                        const [startH, startM] = booking.start_time.split(':').map(Number);
                        const [endH, endM] = booking.end_time.split(':').map(Number);
                        durationMinutes = (endH * 60 + endM) - (startH * 60 + startM);
                        console.log(`⏱️ Calculated duration for ${booking.client_name}: ${booking.start_time} to ${booking.end_time} = ${durationMinutes} minutes (was ${booking.duration})`);
                    }
                    const durationHours = durationMinutes / 60;
                    const width = Math.max(durationHours * 140, 80);
                    
                    // Determine service type for color coding
                    let serviceType = 'default';
                    const serviceName = (booking.service_name || '').toLowerCase();
                    
                    if (serviceName.includes('massage')) {
                        serviceType = 'service-massage';
                    } else if (serviceName.includes('facial')) {
                        serviceType = 'service-facial';
                    } else if (serviceName.includes('manicure')) {
                        serviceType = 'service-manicure';
                    } else if (serviceName.includes('pedicure')) {
                        serviceType = 'service-pedicure';
                    } else if (serviceName.includes('hair') || serviceName.includes('cut')) {
                        serviceType = 'service-haircut';
                    } else if (serviceName.includes('wax')) {
                        serviceType = 'service-waxing';
                    } else {
                        serviceType = 'service-default';
                    }

                    // Create appointment element with service-based color class
                    const appointmentDiv = document.createElement('div');
                    const checkedInClass = booking.checked_in ? 'checked-in' : '';
                    appointmentDiv.className = `appointment-block ${serviceType} ${checkedInClass}`;
                    appointmentDiv.style.left = `${leftPosition}px`;
                    appointmentDiv.style.width = `${width}px`;
                    appointmentDiv.dataset.appointmentId = booking.id;
                    appointmentDiv.dataset.checkedIn = booking.checked_in ? 'true' : 'false';
                    appointmentDiv.draggable = true;

                    appointmentDiv.innerHTML = `
                        <div class="appointment-header">
                            <div class="appointment-client">${booking.client_name}</div>
                            <div class="appointment-status"></div>
                        </div>
                        <div class="appointment-service">${booking.service_names || booking.service_name || 'Service'}</div>
                        <div class="appointment-footer">
                            <div class="appointment-time">
                                <i class="fas fa-clock"></i>${booking.start_time}
                            </div>
                            <div class="appointment-duration">${durationMinutes}m</div>
                        </div>
                    `;

                    row.appendChild(appointmentDiv);
                });

                // Reinitialize context menu
                if (window.appointmentContextMenu?.reinitializeForAppointments) {
                    window.appointmentContextMenu.reinitializeForAppointments();
                }
            }

            function renderShiftOverlays(staffData) {
                document.querySelectorAll(".shift-overlay").forEach(el => el.remove());
                if (!staffData?.length) return;

                staffData.forEach(staff => {
                    const row = document.querySelector(`.timeline-row[data-staff-id="${staff.id}"]`);
                    if (!row) return;

                    const timeToPosition = (timeStr) => {
                        if (!timeStr) return 0;
                        const [hours, minutes] = timeStr.split(':').map(Number);
                        return (hours - 9 + minutes / 60) * 140;
                    };

                    const calculateWidth = (startTime, endTime) => {
                        if (!startTime || !endTime) return 0;
                        const [startH, startM] = startTime.split(':').map(Number);
                        const [endH, endM] = endTime.split(':').map(Number);
                        return Math.max(0, ((endH * 60 + endM) - (startH * 60 + startM)) / 60 * 140);
                    };

                    const createOverlay = (type, left, width, label) => {
                        const overlay = document.createElement('div');
                        overlay.className = `shift-overlay shift-overlay-${type}`;
                        overlay.style.left = `${left}px`;
                        overlay.style.width = `${width}px`;
                        overlay.innerHTML = `<span class="overlay-label">${label}</span>`;
                        return overlay;
                    };

                    // Holiday/Off-day overlays
                    const HOLIDAY_STATUSES = ['holiday'];
                    const OFFDAY_STATUSES = ['off', 'absent', 'leave', 'weekoff', 'not_scheduled', 'offday'];

                    if (staff.day_status && HOLIDAY_STATUSES.includes(staff.day_status)) {
                        row.appendChild(createOverlay('holiday', 0, 13 * 140, 'Holiday'));
                        return;
                    }

                    if (!staff.is_working || !staff.shift_start || !staff.shift_end ||
                        (staff.day_status && OFFDAY_STATUSES.includes(staff.day_status))) {
                        row.appendChild(createOverlay('off-duty', 0, 13 * 140, 'Off Day'));
                        return;
                    }

                    // Before/After shift overlays
                    if (staff.shift_start && staff.shift_start !== '09:00') {
                        const width = timeToPosition(staff.shift_start);
                        if (width > 0) row.appendChild(createOverlay('off-duty', 0, width, 'Before Shift'));
                    }

                    if (staff.shift_end && staff.shift_end !== '22:00') {
                        const left = timeToPosition(staff.shift_end);
                        const width = 13 * 140 - left;
                        if (width > 0) row.appendChild(createOverlay('off-duty', left, width, 'After Shift'));
                    }

                    // Break overlays
                    if (staff.breaks?.length) {
                        staff.breaks.forEach(breakTime => {
                            if (breakTime?.start && breakTime?.end) {
                                const left = timeToPosition(breakTime.start);
                                const width = calculateWidth(breakTime.start, breakTime.end);
                                if (width > 0) row.appendChild(createOverlay('break', left, width, 'Break Time'));
                            }
                        });
                    }

                    // Out-of-office overlays
                    if (staff.ooo?.length) {
                        staff.ooo.forEach(oooTime => {
                            if (oooTime?.start && oooTime?.end) {
                                const left = timeToPosition(oooTime.start);
                                const width = calculateWidth(oooTime.start, oooTime.end);
                                if (width > 0) {
                                    const overlay = createOverlay('out-of-office', left, width, oooTime.reason || 'Out of Office');
                                    if (oooTime.reason) overlay.title = oooTime.reason;
                                    row.appendChild(overlay);
                                }
                            }
                        });
                    }
                });
            }

            function updateStats() {
                const total = bookingsData.length;
                const completed = bookingsData.filter(b => b.status === 'completed').length;
                const paid = bookingsData.filter(b => b.payment_status === 'paid').length;
                const pending = bookingsData.filter(b => b.payment_status === 'pending').length;

                document.getElementById('totalBookings').textContent = total;
                document.getElementById('completedBookings').textContent = completed;

                // Log payment status breakdown
                console.log(`📊 Stats Update:
                    Total: ${total}
                    Completed: ${completed}
                    Paid (hidden): ${paid}
                    Pending (visible): ${pending}
                `);
            }

            function updateCurrentTimeLine() {
                const now = new Date();
                const currentHour = now.getHours();
                const currentMinute = now.getMinutes();

                if (currentHour >= 9 && currentHour < 22) {
                    const timeLine = document.getElementById("currentTimeLine");
                    const timeLabel = document.getElementById("currentTimeLabel");
                    const hoursSince9AM = currentHour - 9;
                    const leftPosition = (hoursSince9AM + currentMinute / 60) * 140;

                    timeLabel.textContent = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: true });
                    timeLine.style.left = leftPosition + "px";
                    timeLine.style.display = "block";
                } else {
                    document.getElementById("currentTimeLine").style.display = "none";
                }
            }

            // ==========================================
            // QUICK ADD CLIENT
            // ==========================================
            function openQuickAddClient() {
                const modalEl = document.getElementById("quickAddClientModal");
                const modal = new bootstrap.Modal(modalEl, {
                    backdrop: 'static',
                    keyboard: true
                });
                document.getElementById('quickAddClientForm').reset();
                modal.show();

                // Ensure proper z-index stacking
                setTimeout(() => {
                    if (modalEl) {
                        modalEl.style.zIndex = '1065';
                    }
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    if (backdrops.length > 0) {
                        backdrops[backdrops.length - 1].style.zIndex = '1060';
                    }
                }, 100);
            }

            async function saveQuickClient() {
                console.log('🔵 saveQuickClient() called');

                // Get form values
                const firstName = document.getElementById('quickFirstName').value.trim();
                const lastName = document.getElementById('quickLastName').value.trim();
                const phone = document.getElementById('quickPhone').value.trim();
                const email = document.getElementById('quickEmail').value.trim();
                const gender = document.getElementById('quickGender').value;

                console.log('📋 Form values:', { firstName, lastName, phone, email, gender });

                // Validation
                if (!firstName || !lastName || !phone || !gender) {
                    console.error('❌ Validation failed - missing required fields');
                    showNotification('Please fill in all required fields (First Name, Last Name, Phone, Gender)', 'error');
                    return;
                }

                // Phone validation
                if (phone.length < 10) {
                    console.error('❌ Invalid phone number');
                    showNotification('Please enter a valid phone number (at least 10 digits)', 'error');
                    return;
                }

                console.log('✅ Validation passed');

                // Get save button by ID
                const submitBtn = document.getElementById('saveQuickClientBtn');

                if (!submitBtn) {
                    console.error('❌ Save button not found!');
                    return;
                }

                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';

                const clientData = {
                    first_name: firstName,
                    last_name: lastName,
                    phone: phone,
                    email: email,
                    gender: gender,
                };

                console.log('📤 Sending data to API:', clientData);

                try {
                    const response = await fetch("/api/unaki/quick-add-client", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(clientData),
                    });

                    console.log('📥 Response status:', response.status);

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    console.log('📥 Response data:', result);

                    if (result.success) {
                        console.log('✅ Client saved successfully:', result.client);

                        showNotification(result.message || 'Client added successfully!', 'success');

                        // Close modal
                        const modalEl = document.getElementById('quickAddClientModal');
                        const modal = bootstrap.Modal.getInstance(modalEl);
                        if (modal) {
                            modal.hide();
                        }

                        quickAddForm.reset();
                    } else {
                        console.error('❌ Server returned error:', result.error);
                        showNotification(result.error || 'Failed to create client', 'error');
                    }
                } catch (error) {
                    console.error("❌ Error saving client:", error);
                    showNotification('Failed to create client: ' + error.message, 'error');
                } finally {
                    // Re-enable submit button
                    if (submitBtn) {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalText;
                    }
                    console.log('🔵 saveQuickClient() completed');
                }
            }



            // ==========================================
            // NAVIGATION FUNCTIONS
            // ==========================================
            function navigateDate(days) {
                const date = new Date(currentDate);
                date.setDate(date.getDate() + days);
                window.location.href = `${window.UNAKI_CONFIG.bookingUrl}?date=${date.toISOString().split("T")[0]}`;
            }

            function navigateToToday() {
                window.location.href = `${window.UNAKI_CONFIG.bookingUrl}?date=${new Date().toISOString().split("T")[0]}`;
            }

            function refreshSchedule() {
                loadBookings();
                loadShiftSchedule();
                const btn = event.target.closest(".action-icon");
                if (btn) {
                    btn.style.transform = "rotate(360deg)";
                    setTimeout(() => btn.style.transform = "rotate(0deg)", 600);
                }
            }

            // Handle empty slot clicks - redirect to multi-appointment booking page
            function handleSlotClick(event, staffId, hour, minute) {
                event.preventDefault();
                event.stopPropagation();

                const selectedDate = currentDate;
                const startTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;

                // Redirect to multi-appointment booking page with pre-filled data
                window.location.href = `/multi-appointment-booking?date=${selectedDate}&staff_id=${staffId}&time=${startTime}`;
            }

            function showLoading(show) {
                document.getElementById("loadingOverlay").classList.toggle("show", show);
            }

            function showNotification(message, type) {
                // Replace this with your actual toast implementation if available
                // For now, using alert for simplicity.
                alert(message);
            }

            function hideContextMenu() {
                if (window.appointmentContextMenu) {
                    window.appointmentContextMenu.hideContextMenu();
                }
            }

            function viewAppointmentDetails() {
                if (selectedAppointmentId && window.appointmentContextMenu) {
                    window.appointmentContextMenu.viewAppointment(selectedAppointmentId);
                }
            }

            function editAppointment() {
                if (selectedAppointmentId && window.appointmentContextMenu?.editAppointment) {
                    window.appointmentContextMenu.editAppointment(selectedAppointmentId);
                }
                hideContextMenu();
            }

            function cancelAppointment() {
                if (selectedAppointmentId && confirm("Are you sure you want to cancel this appointment?")) {
                    // Implement cancellation logic here
                    alert("Cancel appointment " + selectedAppointmentId);
                }
                hideContextMenu();
            }

            // ==========================================
            // CHECK-IN FUNCTIONS
            // ==========================================

            function performManualCheckin() {
                const clientSelect = document.getElementById('checkinClientSelect');
                const clientId = clientSelect.value;
                const messageDiv = document.getElementById('checkinMessage');

                if (!clientId) {
                    messageDiv.className = 'alert alert-warning';
                    messageDiv.style.display = 'block';
                    messageDiv.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Please select a client';
                    return;
                }

                messageDiv.style.display = 'none';

                fetch('/api/unaki/checkin/manual', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ client_id: parseInt(clientId) })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        messageDiv.className = 'alert alert-success';
                        messageDiv.style.display = 'block';
                        messageDiv.innerHTML = `<i class="fas fa-check-circle me-2"></i>${data.message}`;

                        setTimeout(() => {
                            bootstrap.Modal.getInstance(document.getElementById('manualCheckinModal')).hide();
                            loadBookings();
                            clientSelect.value = '';
                            messageDiv.style.display = 'none';
                        }, 1500);
                    } else {
                        messageDiv.className = 'alert alert-danger';
                        messageDiv.style.display = 'block';
                        messageDiv.innerHTML = `<i class="fas fa-times-circle me-2"></i>${data.error}`;
                    }
                })
                .catch(error => {
                    console.error('Check-in error:', error);
                    messageDiv.className = 'alert alert-danger';
                    messageDiv.style.display = 'block';
                    messageDiv.innerHTML = '<i class="fas fa-times-circle me-2"></i>Error checking in client';
                });
            }

            function checkinAppointment(appointmentId) {
                if (!appointmentId) {
                    showNotification('No appointment selected', 'error');
                    return;
                }

                fetch(`/api/unaki/checkin/${appointmentId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ ' + data.message, 'success');
                        // Update the appointment block immediately for instant feedback
                        const appointmentBlock = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
                        if (appointmentBlock) {
                            appointmentBlock.classList.add('checked-in');
                            appointmentBlock.dataset.checkedIn = 'true';
                        }
                        // Refresh the full schedule to ensure consistency
                        setTimeout(() => loadBookings(), 500);
                    } else {
                        showNotification('Error: ' + data.error, 'error');
                    }
                })
                .catch(error => {
                    console.error('Check-in error:', error);
                    showNotification('Error checking in appointment', 'error');
                })
                .finally(() => {
                    hideContextMenu();
                });
            }

            function undoCheckin(appointmentId) {
                if (!appointmentId) return;

                fetch(`/api/unaki/checkin/undo/${appointmentId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        loadBookings();
                    } else {
                        showNotification(data.error || 'Failed to undo check-in', 'error');
                    }
                })
                .catch(error => {
                    console.error('Undo check-in error:', error);
                    showNotification('Error undoing check-in', 'error');
                });
                hideContextMenu();
            }

            function saveEditedAppointment() {
                const appointmentId = document.getElementById('editAppointmentId').value;
                const serviceSelect = document.getElementById('editServiceSelect');
                const serviceId = serviceSelect.value;
                const serviceName = serviceSelect.selectedOptions[0]?.text.split(' (')[0].trim();
                const staffId = document.getElementById('editStaffSelect').value;
                const appointmentDate = document.getElementById('editAppointmentDate').value;
                const startTime = document.getElementById('editStartTime').value;
                const endTime = document.getElementById('editEndTime').value;
                const notes = document.getElementById('editNotes').value;
                const status = document.getElementById('editStatus').value;
                const paymentStatus = document.getElementById('editPaymentStatus').value;

                if (!serviceId || !staffId || !appointmentDate || !startTime || !endTime) {
                    showToast('Please fill all required fields', 'error');
                    return;
                }

                const updateData = {
                    service_id: parseInt(serviceId),
                    service_name: serviceName,
                    staff_id: parseInt(staffId),
                    appointment_date: appointmentDate,
                    start_time: startTime,
                    end_time: endTime,
                    notes: notes,
                    status: status,
                    payment_status: paymentStatus
                };

                console.log('💾 Saving appointment with payment status:', paymentStatus, 'and status:', status);

                fetch(`/api/unaki/bookings/${appointmentId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(updateData)
                })
                .then(response => response.json())
                .then(data => {
                    console.log('✅ Update response:', data);
                    if (data.success) {
                        showToast(data.message || 'Appointment updated successfully', 'success');

                        // Show special message if payment status changed to paid and completed
                        if (paymentStatus === 'paid' && status === 'completed') {
                            showToast('Payment marked as paid. Appointment will be hidden from view.', 'info');
                            // Force page reload after 1 second to ensure UI updates
                            setTimeout(() => {
                                window.location.reload();
                            }, 1000);
                        } else {
                            bootstrap.Modal.getInstance(document.getElementById('editAppointmentModal')).hide();
                            loadBookings();
                        }
                    } else {
                        showToast(data.error || 'Failed to update appointment', 'error');
                    }
                })
                .catch(error => {
                    console.error('❌ Error updating appointment:', error);
                    showToast('Error updating appointment', 'error');
                });
            }

            function showEditModal(appointmentData) {
                console.log('✏️ Showing edit appointment modal:', appointmentData);

                // Populate form fields
                document.getElementById('editAppointmentId').value = appointmentData.id;
                document.getElementById('editClientName').value = appointmentData.client_name;
                document.getElementById('editAppointmentDate').value = appointmentData.appointment_date;
                document.getElementById('editStartTime').value = appointmentData.start_time;
                document.getElementById('editEndTime').value = appointmentData.end_time;
                document.getElementById('editNotes').value = appointmentData.notes || '';

                // Set service dropdown
                const serviceSelect = document.getElementById('editServiceSelect');
                if (appointmentData.service_id) {
                    serviceSelect.value = appointmentData.service_id;
                    // Trigger change event to ensure end time is calculated if needed
                    serviceSelect.dispatchEvent(new Event('change'));
                }

                // Set staff dropdown
                const staffSelect = document.getElementById('editStaffSelect');
                staffSelect.value = appointmentData.staff_id;

                // Set status dropdown
                const statusSelect = document.getElementById('editStatus');
                statusSelect.value = appointmentData.status || 'scheduled';

                // Set payment status dropdown
                const paymentStatusSelect = document.getElementById('editPaymentStatus');
                paymentStatusSelect.value = appointmentData.payment_status || 'pending';

                // Show modal
                const editModal = new bootstrap.Modal(document.getElementById('editAppointmentModal'));
                editModal.show();

                // Update end time when service changes
                serviceSelect.addEventListener('change', function() {
                    const selectedOption = this.options[this.selectedIndex];
                    const duration = parseInt(selectedOption.dataset.duration) || 60;
                    const startTime = document.getElementById('editStartTime').value;

                    if (startTime) {
                        const endTime = calculateEndTimeFromDuration(startTime, duration);
                        document.getElementById('editEndTime').value = endTime;
                    }
                });

                // Update end time when start time changes
                document.getElementById('editStartTime').addEventListener('change', function() {
                    const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
                    const duration = parseInt(selectedOption.dataset.duration) || 60;
                    const endTime = calculateEndTimeFromDuration(this.value, duration);
                    document.getElementById('editEndTime').value = endTime;
                });
            }

            // Helper function to calculate end time based on start time and duration
            function calculateEndTimeFromDuration(startTime, durationMinutes) {
                const [hours, minutes] = startTime.split(':').map(Number);
                const startDate = new Date();
                startDate.setHours(hours, minutes, 0, 0);
                const endDate = new Date(startDate.getTime() + durationMinutes * 60000);
                return endDate.toTimeString().slice(0, 5);
            }

            // Helper function to show toast notifications (if you have a toast library integrated)
            function showToast(message, type = 'info') {
                // Replace this with your actual toast implementation
                console.log(`Toast (${type}): ${message}`);
                alert(`${type.toUpperCase()}: ${message}`);
            }

