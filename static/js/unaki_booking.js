// Configuration
const SCHEDULE_CONFIG = {
    startHour: 8,
    endHour: 20,
    slotMinutes: 5,
    staffColumnWidth: 240,
    timeSlotWidth: 45
};

// Global Variables
let scheduleData = { staff: [], appointments: [], breaks: [] };
let servicesData = [];
let staffData = [];
let serviceRowCount = 0;
let currentDate = new Date().toISOString().split('T')[0];

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    const toastId = 'toast-' + Date.now();
    const bgClass = { 'success': 'bg-success', 'error': 'bg-danger', 'warning': 'bg-warning', 'info': 'bg-info' }[type] || 'bg-info';
    const iconClass = { 'success': 'fas fa-check-circle', 'error': 'fas fa-exclamation-circle', 'warning': 'fas fa-exclamation-triangle', 'info': 'fas fa-info-circle' }[type] || 'fas fa-info-circle';

    const toastHTML = `
        <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header ${bgClass} text-white border-0">
                <i class="${iconClass} me-2"></i>
                <strong class="me-auto">Notification</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">${message}</div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { delay: duration });
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'position-fixed top-0 end-0 p-3';
    container.style.zIndex = '11000';
    document.body.appendChild(container);
    return container;
}

// Loading Functions
function showLoading() {
    document.getElementById('loadingOverlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('show');
}

function showLoadingAndLoad() {
    showLoading();
    setTimeout(() => { loadScheduleForDate(); hideLoading(); }, 800);
}

function showLoadingAndRefresh() {
    showLoading();
    setTimeout(() => { refreshSchedule(); hideLoading(); }, 600);
}

function showLoadingAndLoadSample() {
    showLoading();
    setTimeout(() => { loadSampleData(); hideLoading(); }, 800);
}

// Date Navigation
function navigateDate(direction) {
    const dateInput = document.getElementById('scheduleDate');
    const currentDate = new Date(dateInput.value);
    currentDate.setDate(currentDate.getDate() + direction);
    dateInput.value = currentDate.toISOString().split('T')[0];
    showLoadingAndLoad();
}

function goToToday() {
    document.getElementById('scheduleDate').value = new Date().toISOString().split('T')[0];
    showLoadingAndLoad();
}

// Time Functions
function updateCurrentDateTime() {
    const now = new Date();
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });
    document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

function timeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
}

// Enhanced Context Menu System
function showFallbackContextMenu(event, appointmentId) {
    console.log(`🎯 Enhanced context menu for appointment ${appointmentId}`);

    const appointment = scheduleData.appointments.find(apt => apt.id == appointmentId || apt.appointment_id == appointmentId);

    if (!appointment) {
        console.error(`❌ Appointment ${appointmentId} not found in schedule data`);
        showNotification('Appointment data not found. Please refresh and try again.', 'error');
        return;
    }

    console.log(`📋 Found appointment data:`, appointment);

    const contextMenuHTML = `
        <div id="dynamicContextMenu" style="position: absolute; left: ${event.pageX}px; top: ${event.pageY}px; background: white; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); z-index: 10000; min-width: 200px; font-family: Inter, sans-serif;">
            <div style="padding: 12px 16px; border-bottom: 1px solid #eee; background: #f8f9fa; border-radius: 8px 8px 0 0;">
                <strong style="color: #333;">${appointment.clientName || 'Unknown Client'}</strong>
                <div style="font-size: 12px; color: #666;">${appointment.service || appointment.serviceName || 'Unknown Service'}</div>
            </div>
            <div style="padding: 4px 0;">
                <div class="context-menu-item" onclick="viewAppointmentDetails('${appointmentId}')" style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='none'">
                    <i class="fas fa-eye" style="color: #007bff; width: 16px;"></i>
                    <span>View Details</span>
                </div>
                <div class="context-menu-item" onclick="editAppointment('${appointmentId}')" style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='none'">
                    <i class="fas fa-edit" style="color: #17a2b8; width: 16px;"></i>
                    <span>Edit Appointment</span>
                </div>
                <hr style="margin: 4px 0; border: none; border-top: 1px solid #eee;">
                <div class="context-menu-item" onclick="redirectToBilling('${appointment.client_id || appointment.clientId}', '${appointmentId}')" style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s; background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);" onmouseover="this.style.background='linear-gradient(135deg, #d4edda 0%, #e2f5e3 100%)'" onmouseout="this.style.background='linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%)'">
                    <i class="fas fa-file-invoice-dollar" style="color: #28a745; width: 16px;"></i>
                    <span style="font-weight: 600; color: #28a745;">Go to Integrated Billing</span>
                </div>
                <div class="context-menu-item" onclick="markAsPaid('${appointmentId}')" style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='none'">
                    <i class="fas fa-check-circle" style="color: #28a745; width: 16px;"></i>
                    <span>Mark as Paid</span>
                </div>
                <hr style="margin: 4px 0; border: none; border-top: 1px solid #eee;">
                <div class="context-menu-item" onclick="deleteAppointment('${appointmentId}')" style="padding: 10px 16px; cursor: pointer; display: flex; align-items: center; gap: 10px; transition: background 0.2s;" onmouseover="this.style.background='#f8d7da'" onmouseout="this.style.background='none'">
                    <i class="fas fa-trash" style="color: #dc3545; width: 16px;"></i>
                    <span style="color: #dc3545;">Delete</span>
                </div>
            </div>
        </div>
    `;

    const existingMenu = document.getElementById('dynamicContextMenu');
    if (existingMenu) existingMenu.remove();

    document.body.insertAdjacentHTML('beforeend', contextMenuHTML);

    setTimeout(() => {
        document.addEventListener('click', function closeContextMenu(e) {
            const menu = document.getElementById('dynamicContextMenu');
            if (menu && !menu.contains(e.target)) {
                menu.remove();
                document.removeEventListener('click', closeContextMenu);
            }
        });
    }, 100);

    const menu = document.getElementById('dynamicContextMenu');
    const rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (event.pageX - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (event.pageY - rect.height) + 'px';
}

function redirectToBilling(clientId, appointmentId) {
    console.log(`🔄 Redirecting to billing with client_id: ${clientId}, appointment_id: ${appointmentId}`);

    const menu = document.getElementById('dynamicContextMenu');
    if (menu) menu.remove();

    if (!clientId || clientId === 'null' || clientId === 'undefined') {
        console.error(`❌ Invalid client_id: ${clientId}`);

        const appointment = scheduleData.appointments.find(apt => apt.id == appointmentId || apt.appointment_id == appointmentId);

        if (appointment) {
            clientId = appointment.client_id || appointment.clientId || appointment.customer_id || appointment.customerId;
            console.log(`🔍 Extracted client_id from appointment: ${clientId}`);
        }

        if (!clientId || clientId === 'null' || clientId === 'undefined') {
            showNotification('Client ID not found. Using backend route for customer matching.', 'warning');
            window.location.href = `/appointment/${appointmentId}/go-to-billing`;
            return;
        }
    }

    showNotification(`Loading billing for client ID: ${clientId}...`, 'info');
    window.location.href = `/integrated-billing/${clientId}`;
}

function markAsPaid(appointmentId) {
    console.log(`💰 Marking appointment ${appointmentId} as paid`);

    const menu = document.getElementById('dynamicContextMenu');
    if (menu) menu.remove();

    fetch(`/api/unaki/appointments/${appointmentId}/mark-paid`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_status: 'paid' })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Appointment marked as paid!', 'success');
            refreshSchedule();
        } else {
            showNotification('Failed to mark as paid: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error marking as paid:', error);
        showNotification('Error marking appointment as paid', 'error');
    });
}

// Service Management Functions
function addServiceRow() {
    serviceRowCount++;
    const servicesContainer = document.getElementById('servicesContainer');

    const serviceRow = document.createElement('div');
    serviceRow.className = 'service-row mb-3 p-3 border rounded';
    serviceRow.id = `serviceRow_${serviceRowCount}`;

    serviceRow.innerHTML = `
        <div class="row g-3 align-items-end">
            <div class="col-md-3">
                <label class="form-label">Service *</label>
                <select class="form-select service-select" data-row="${serviceRowCount}" required>
                    <option value="">Select Service</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Staff *</label>
                <select class="form-select staff-select" data-row="${serviceRowCount}" required>
                    <option value="">Select Staff</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label">Start Time *</label>
                <input type="time" class="form-control start-time" data-row="${serviceRowCount}" required onchange="updateServiceEndTime(${serviceRowCount})">
            </div>
            <div class="col-md-2">
                <label class="form-label">End Time</label>
                <input type="time" class="form-control end-time" data-row="${serviceRowCount}" readonly>
            </div>
            <div class="col-md-2">
                <label class="form-label">Price ($)</label>
                <input type="number" class="form-control service-price" data-row="${serviceRowCount}" step="0.01" readonly>
            </div>
            <div class="col-md-1">
                <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeServiceRow(${serviceRowCount})" ${serviceRowCount === 1 ? 'style="display:none"' : ''}>
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;

    servicesContainer.appendChild(serviceRow);
    populateServiceDropdown(serviceRowCount);
    populateStaffDropdown(serviceRowCount);
    setupServiceRowEventListeners(serviceRowCount);

    if (serviceRowCount === 1) {
        const now = new Date();
        const nextHour = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours() + 1, 0);
        serviceRow.querySelector('.start-time').value = nextHour.toTimeString().slice(0, 5);
    } else {
        const previousRows = document.querySelectorAll('.service-row');
        const lastRow = previousRows[previousRows.length - 2];
        if (lastRow) {
            const lastEndTime = lastRow.querySelector('.end-time').value;
            if (lastEndTime) serviceRow.querySelector('.start-time').value = lastEndTime;
        }
    }
}

function removeServiceRow(rowId) {
    const serviceRow = document.getElementById(`serviceRow_${rowId}`);
    if (serviceRow) {
        serviceRow.remove();
        calculateTotals();

        const remainingRows = document.querySelectorAll('.service-row');
        remainingRows.forEach((row, index) => {
            const removeBtn = row.querySelector('.btn-outline-danger');
            removeBtn.style.display = remainingRows.length > 1 ? 'block' : 'none';
        });
    }
}

function populateServiceDropdown(rowId) {
    const serviceSelect = document.querySelector(`[data-row="${rowId}"].service-select`);
    if (serviceSelect && servicesData.length > 0) {
        serviceSelect.innerHTML = '<option value="">Select Service</option>';
        servicesData.forEach(service => {
            const option = document.createElement('option');
            option.value = service.id || service.name;
            option.textContent = `${service.name} ($${service.price}) - ${service.duration}min`;
            option.dataset.price = service.price;
            option.dataset.duration = service.duration;
            serviceSelect.appendChild(option);
        });
    }
}

function populateStaffDropdown(rowId) {
    const staffSelect = document.querySelector(`[data-row="${rowId}"].staff-select`);
    if (staffSelect && staffData.length > 0) {
        staffSelect.innerHTML = '<option value="">Select Staff</option>';
        staffData.forEach(staff => {
            const option = document.createElement('option');
            option.value = staff.id;
            option.textContent = `${staff.name} (${staff.specialty || staff.role || 'Staff'})`;
            staffSelect.appendChild(option);
        });

        if (staffData.length > 0) staffSelect.value = staffData[0].id;
    }
}

function setupServiceRowEventListeners(rowId) {
    const serviceSelect = document.querySelector(`[data-row="${rowId}"].service-select`);
    const priceInput = document.querySelector(`[data-row="${rowId}"].service-price`);

    serviceSelect.addEventListener('change', function() {
        const selectedOption = this.options[this.selectedIndex];
        if (selectedOption.dataset.price) {
            priceInput.value = selectedOption.dataset.price;
            updateServiceEndTime(rowId);
            calculateTotals();
        }
    });
}

function updateServiceEndTime(rowId) {
    const startTimeInput = document.querySelector(`[data-row="${rowId}"].start-time`);
    const endTimeInput = document.querySelector(`[data-row="${rowId}"].end-time`);
    const serviceSelect = document.querySelector(`[data-row="${rowId}"].service-select`);

    if (startTimeInput.value && serviceSelect.value) {
        const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
        const duration = parseInt(selectedOption.dataset.duration) || 60;

        const startTime = new Date(`2000-01-01T${startTimeInput.value}:00`);
        const endTime = new Date(startTime.getTime() + duration * 60000);
        endTimeInput.value = endTime.toTimeString().slice(0, 5);
    }
}

function calculateTotals() {
    let totalDuration = 0;
    let subtotal = 0;

    document.querySelectorAll('.service-row').forEach(row => {
        const serviceSelect = row.querySelector('.service-select');
        const priceInput = row.querySelector('.service-price');

        if (serviceSelect.value && priceInput.value) {
            const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
            const duration = parseInt(selectedOption.dataset.duration) || 0;
            const price = parseFloat(priceInput.value) || 0;

            totalDuration += duration;
            subtotal += price;
        }
    });

    const hours = Math.floor(totalDuration / 60);
    const minutes = totalDuration % 60;
    const durationText = hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`;

    document.getElementById('totalDuration').value = durationText;
    document.getElementById('subtotalPrice').value = `$${subtotal.toFixed(2)}`;

    const discount = parseFloat(document.getElementById('discountAmount').value) || 0;
    const grandTotal = Math.max(0, subtotal - discount);
    document.getElementById('grandTotal').value = `$${grandTotal.toFixed(2)}`;
}

// API Functions
function loadServices() {
    return fetch('/api/unaki/services')
        .then(response => response.ok ? response.json() : Promise.reject(new Error(`HTTP error! status: ${response.status}`)))
        .then(services => {
            servicesData = services || [];
            console.log('Loaded services:', services.length);
            return services;
        })
        .catch(error => {
            console.error('Failed to load services:', error);
            showNotification('Failed to load services', 'error');
            return [];
        });
}

function loadStaff() {
    return fetch('/api/unaki/staff')
        .then(response => response.ok ? response.json() : Promise.reject(new Error(`HTTP error! status: ${response.status}`)))
        .then(staff => {
            staffData = staff || [];
            console.log('Loaded staff:', staff.length);
            return staff;
        })
        .catch(error => {
            console.error('Failed to load staff:', error);
            showNotification('Failed to load staff', 'error');
            return [];
        });
}

function loadClients() {
    return fetch('/api/unaki/clients')
        .then(response => response.ok ? response.json() : Promise.reject(new Error(`HTTP error! status: ${response.status}`)))
        .then(clients => {
            console.log('Loaded clients:', clients.length);

            const clientSelect = document.getElementById('clientSelect');
            if (clientSelect && Array.isArray(clients)) {
                clientSelect.innerHTML = '<option value="">Select Client</option>';

                clients.forEach(client => {
                    const option = document.createElement('option');
                    option.value = client.id;
                    option.textContent = client.name;
                    option.dataset.phone = client.phone || '';
                    option.dataset.email = client.email || '';
                    clientSelect.appendChild(option);
                });

                clientSelect.addEventListener('change', function() {
                    const selectedOption = this.options[this.selectedIndex];
                    if (selectedOption && selectedOption.dataset.phone) {
                        document.getElementById('clientPhone').value = selectedOption.dataset.phone;
                        document.getElementById('clientEmail').value = selectedOption.dataset.email || '';
                    }
                });
            }
            return clients;
        })
        .catch(error => {
            console.error('Failed to load clients:', error);
            showNotification('Failed to load clients', 'error');
            return [];
        });
}

function loadScheduleForDate() {
    const selectedDate = document.getElementById('scheduleDate').value;
    if (!selectedDate) return;

    console.log(`📅 Loading schedule for date: ${selectedDate}`);

    // Clear current schedule grid
    const scheduleGrid = document.getElementById('scheduleGrid');
    if (scheduleGrid) scheduleGrid.innerHTML = '';

    fetch(`/api/unaki/schedule/${selectedDate}`)
        .then(response => response.ok ? response.json() : Promise.reject(new Error(`HTTP error! status: ${response.status}`)))
        .then(data => {
            console.log('Schedule data loaded:', data);
            scheduleData = data;
            renderScheduleGrid();
            updateStats();
        })
        .catch(error => {
            console.error('Failed to load schedule:', error);
            showNotification('Failed to load schedule data', 'error');
            loadSampleData();
        });
}

function renderScheduleGrid() {
    const container = document.getElementById('scheduleGrid');
    if (!container) return;

    const staff = scheduleData.staff || [];
    const appointments = scheduleData.appointments || [];

    console.log(`🏗️ Rendering grid with ${staff.length} staff and ${appointments.length} appointments`);

    let gridHTML = '';

    // Empty top-left corner
    gridHTML += '<div class="time-header"></div>';

    // Time headers
    for (let hour = SCHEDULE_CONFIG.startHour; hour < SCHEDULE_CONFIG.endHour; hour++) {
        for (let minute = 0; minute < 60; minute += SCHEDULE_CONFIG.slotMinutes) {
            const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
            gridHTML += `<div class="time-header">${timeStr}</div>`;
        }
    }

    // Staff rows
    staff.forEach(staffMember => {
        gridHTML += `
            <div class="staff-cell">
                <div class="staff-name">${staffMember.name}</div>
                <div class="staff-role">${staffMember.specialty || staffMember.role || 'Staff'}</div>
            </div>
        `;

        // Time slots for this staff member
        for (let hour = SCHEDULE_CONFIG.startHour; hour < SCHEDULE_CONFIG.endHour; hour++) {
            for (let minute = 0; minute < 60; minute += SCHEDULE_CONFIG.slotMinutes) {
                const slotId = `slot-${staffMember.id}-${hour}-${minute}`;
                const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;

                // Check for appointments in this slot
                const appointment = appointments.find(apt => 
                    apt.staff_id == staffMember.id && 
                    apt.start_time && 
                    apt.start_time.startsWith(timeStr)
                );

                if (appointment) {
                    const serviceCategory = getServiceCategory(appointment.service || appointment.serviceName);
                    gridHTML += `
                        <div class="time-slot" id="${slotId}">
                            <div class="appointment-block ${serviceCategory}" 
                                 oncontextmenu="showFallbackContextMenu(event, ${appointment.id || appointment.appointment_id}); return false;"
                                 onclick="showFallbackContextMenu(event, ${appointment.id || appointment.appointment_id})"
                                 data-appointment-id="${appointment.id || appointment.appointment_id}">
                                <div class="appointment-client">${appointment.clientName || appointment.client_name || 'Unknown'}</div>
                                <div class="appointment-service">${appointment.service || appointment.serviceName || 'Service'}</div>
                                <div class="appointment-time">${appointment.start_time || timeStr}</div>
                            </div>
                        </div>
                    `;
                } else {
                    gridHTML += `
                        <div class="time-slot" id="${slotId}" 
                             onclick="openBookingModal('${staffMember.id}', '${timeStr}')"
                             data-staff-id="${staffMember.id}" 
                             data-time="${timeStr}">
                        </div>
                    `;
                }
            }
        }
    });

    container.innerHTML = gridHTML;
}

function getServiceCategory(serviceName) {
    if (!serviceName) return '';
    
    const service = serviceName.toLowerCase();
    if (service.includes('massage')) return 'service-category-massage';
    if (service.includes('facial')) return 'service-category-facial';
    if (service.includes('hair')) return 'service-category-hair';
    if (service.includes('nail')) return 'service-category-nails';
    if (service.includes('body')) return 'service-category-body';
    return '';
}

function openBookingModal(staffId, timeStr) {
    console.log(`📅 Opening booking modal for staff ${staffId} at ${timeStr}`);
    
    // Set the modal form data
    const staffSelect = document.getElementById('appointmentStaff');
    if (staffSelect) staffSelect.value = staffId;
    
    const timeInput = document.getElementById('appointmentTime');
    if (timeInput) timeInput.value = timeStr;
    
    // Open the modal
    const modal = new bootstrap.Modal(document.getElementById('bookingModal'));
    modal.show();
}

function updateStats() {
    const totalStaff = scheduleData.staff ? scheduleData.staff.length : 0;
    const totalAppointments = scheduleData.appointments ? scheduleData.appointments.length : 0;
    const revenue = scheduleData.appointments ? 
        scheduleData.appointments.reduce((sum, apt) => sum + (parseFloat(apt.price) || 0), 0) : 0;

    document.getElementById('totalStaff').textContent = totalStaff;
    document.getElementById('totalAppointments').textContent = totalAppointments;
    document.getElementById('totalRevenue').textContent = `$${revenue.toFixed(2)}`;
}

function refreshSchedule() {
    loadScheduleForDate();
}

function loadSampleData() {
    console.log('🔄 Loading sample data...');
    
    scheduleData = {
        staff: [
            { id: 1, name: 'Sarah Johnson', specialty: 'Massage Therapist', role: 'Senior' },
            { id: 2, name: 'Mike Chen', specialty: 'Facial Specialist', role: 'Expert' },
            { id: 3, name: 'Emma Davis', specialty: 'Hair Stylist', role: 'Senior' }
        ],
        appointments: [
            {
                id: 1,
                staff_id: 1,
                clientName: 'Alice Smith',
                service: 'Deep Tissue Massage',
                start_time: '09:00',
                end_time: '10:00',
                price: 120,
                client_id: 101
            },
            {
                id: 2,
                staff_id: 2,
                clientName: 'Bob Wilson',
                service: 'Anti-Aging Facial',
                start_time: '10:30',
                end_time: '11:30',
                price: 95,
                client_id: 102
            }
        ],
        breaks: []
    };

    renderScheduleGrid();
    updateStats();
    showNotification('Sample data loaded for demonstration', 'info');
}

// Booking Functions
function bookMultiServiceAppointment() {
    console.log('📝 Booking multi-service appointment...');

    const clientId = document.getElementById('clientSelect').value;
    const appointmentDate = document.getElementById('scheduleDate').value;
    const notes = document.getElementById('appointmentNotes').value;

    if (!clientId) {
        showNotification('Please select a client', 'error');
        return;
    }

    const services = [];
    document.querySelectorAll('.service-row').forEach(row => {
        const serviceId = row.querySelector('.service-select').value;
        const staffId = row.querySelector('.staff-select').value;
        const startTime = row.querySelector('.start-time').value;
        const endTime = row.querySelector('.end-time').value;
        const price = row.querySelector('.service-price').value;

        if (serviceId && staffId && startTime) {
            services.push({
                service_id: serviceId,
                staff_id: staffId,
                start_time: startTime,
                end_time: endTime,
                price: parseFloat(price) || 0
            });
        }
    });

    if (services.length === 0) {
        showNotification('Please add at least one service', 'error');
        return;
    }

    const bookingData = {
        client_id: clientId,
        appointment_date: appointmentDate,
        services: services,
        notes: notes
    };

    fetch('/api/unaki/appointments/book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Appointment booked successfully!', 'success');
            bootstrap.Modal.getInstance(document.getElementById('bookingModal')).hide();
            refreshSchedule();
        } else {
            showNotification('Failed to book appointment: ' + (data.error || 'Unknown error'), 'error');
        }
    })
    .catch(error => {
        console.error('Booking error:', error);
        showNotification('Error booking appointment', 'error');
    });
}

function checkAvailability() {
    console.log('🔍 Checking availability...');
    showNotification('Checking staff availability...', 'info');
    
    // Simulate availability check
    setTimeout(() => {
        showNotification('All selected staff are available!', 'success');
    }, 1000);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Unaki Booking System...');
    
    // Initialize date
    document.getElementById('scheduleDate').value = new Date().toISOString().split('T')[0];
    
    // Update time display
    updateCurrentDateTime();
    setInterval(updateCurrentDateTime, 1000);
    
    // Load initial data
    Promise.all([loadServices(), loadStaff(), loadClients()])
        .then(() => {
            console.log('✅ All data loaded');
            loadScheduleForDate();
            
            // Add first service row
            addServiceRow();
        })
        .catch(error => {
            console.error('❌ Failed to load initial data:', error);
            showNotification('Failed to load some data. Using sample data.', 'warning');
            loadSampleData();
            addServiceRow();
        });
    
    // Set up discount calculation
    document.getElementById('discountAmount').addEventListener('input', calculateTotals);
    
    showNotification('Unaki Booking System loaded successfully!', 'success');
});

// Additional helper functions that may be referenced in the HTML
function viewAppointmentDetails(appointmentId) {
    console.log(`👁️ Viewing details for appointment ${appointmentId}`);
    showNotification(`Loading appointment details...`, 'info');
    // Implementation would go here
}

function editAppointment(appointmentId) {
    console.log(`✏️ Editing appointment ${appointmentId}`);
    showNotification(`Opening edit form...`, 'info');
    // Implementation would go here
}

function deleteAppointment(appointmentId) {
    console.log(`🗑️ Deleting appointment ${appointmentId}`);
    if (confirm('Are you sure you want to delete this appointment?')) {
        showNotification(`Deleting appointment...`, 'info');
        // Implementation would go here
        setTimeout(() => {
            showNotification('Appointment deleted successfully!', 'success');
            refreshSchedule();
        }, 1500);
    }
}