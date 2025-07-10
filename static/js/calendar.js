// Calendar and booking management functionality

class BookingCalendar {
    constructor() {
        this.selectedDate = new Date();
        this.currentView = 'day';
        this.appointments = [];
        this.staff = [];
        this.services = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadCalendarData();
        this.updateCalendarView();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // Date navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.prev-day')) {
                this.navigateDay(-1);
            } else if (e.target.matches('.next-day')) {
                this.navigateDay(1);
            } else if (e.target.matches('.today-btn')) {
                this.goToToday();
            }
        });

        // View switching
        document.addEventListener('change', (e) => {
            if (e.target.matches('#calendarView')) {
                this.changeView(e.target.value);
            }
        });

        // Appointment actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('.appointment-block')) {
                this.showAppointmentDetails(e.target.dataset.appointmentId);
            } else if (e.target.matches('.time-slot')) {
                this.showNewAppointmentModal(e.target.dataset.time);
            }
        });

        // Form submissions
        const appointmentForm = document.getElementById('appointmentForm');
        if (appointmentForm) {
            appointmentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleAppointmentSubmit(e.target);
            });
        }

        // Real-time updates (every 30 seconds)
        setInterval(() => {
            this.refreshAppointments();
        }, 30000);
    }

    loadCalendarData() {
        // Load staff data
        this.loadStaffData();
        
        // Load services data
        this.loadServicesData();
        
        // Load appointments for current date
        this.loadAppointments();
    }

    loadStaffData() {
        // This would normally fetch from server
        // For now, get from existing form data
        const staffSelect = document.getElementById('staff_id');
        if (staffSelect) {
            this.staff = Array.from(staffSelect.options).map(option => ({
                id: option.value,
                name: option.text,
                color: this.generateStaffColor(option.value)
            })).filter(staff => staff.id);
        }
    }

    loadServicesData() {
        // Load from existing form data
        const serviceSelect = document.getElementById('service_id');
        if (serviceSelect) {
            this.services = Array.from(serviceSelect.options).map(option => ({
                id: option.value,
                name: option.text.split(' - ')[0],
                price: option.text.includes('$') ? option.text.split('$')[1] : '0',
                duration: 60 // Default duration
            })).filter(service => service.id);
        }
    }

    loadAppointments() {
        // In a production app, this would fetch from the server
        // For now, parse existing appointments from the page
        const appointmentRows = document.querySelectorAll('tbody tr');
        this.appointments = [];
        
        appointmentRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 6) {
                const timeText = cells[0].textContent.trim();
                const clientName = cells[1].querySelector('div')?.textContent.trim();
                const serviceName = cells[2].textContent.trim();
                const staffName = cells[3].textContent.trim();
                const amount = cells[5].textContent.trim();
                const status = cells[6].querySelector('.badge')?.textContent.trim();

                if (timeText && clientName) {
                    this.appointments.push({
                        id: Math.random().toString(36).substr(2, 9),
                        time: timeText,
                        clientName: clientName,
                        serviceName: serviceName,
                        staffName: staffName,
                        amount: amount,
                        status: status?.toLowerCase().replace(' ', '_') || 'scheduled',
                        date: this.selectedDate.toISOString().split('T')[0]
                    });
                }
            }
        });

        this.renderAppointments();
    }

    updateCalendarView() {
        const dateElement = document.querySelector('.current-date');
        if (dateElement) {
            const options = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            };
            dateElement.textContent = this.selectedDate.toLocaleDateString('en-US', options);
        }
    }

    renderAppointments() {
        if (this.currentView === 'day') {
            this.renderDayView();
        } else if (this.currentView === 'week') {
            this.renderWeekView();
        }
    }

    renderDayView() {
        let calendarContainer = document.getElementById('dayViewContainer');
        if (!calendarContainer) {
            // Create day view if it doesn't exist
            this.createDayViewContainer();
            calendarContainer = document.getElementById('dayViewContainer');
        }

        const timeSlots = this.generateTimeSlots();
        let html = '<div class="day-calendar">';

        // Header with staff columns
        html += '<div class="calendar-header">';
        html += '<div class="time-column">Time</div>';
        this.staff.forEach(staff => {
            html += `<div class="staff-column" style="border-left: 3px solid ${staff.color}">${staff.name}</div>`;
        });
        html += '</div>';

        // Time slots
        timeSlots.forEach(time => {
            html += `<div class="time-row" data-time="${time}">`;
            html += `<div class="time-label">${this.formatTime(time)}</div>`;
            
            this.staff.forEach(staff => {
                const appointment = this.getAppointmentAt(time, staff.id);
                html += `<div class="time-slot ${appointment ? 'occupied' : 'available'}" 
                            data-time="${time}" 
                            data-staff="${staff.id}"
                            style="border-left: 3px solid ${staff.color}">`;
                
                if (appointment) {
                    html += this.renderAppointmentBlock(appointment);
                } else {
                    html += `<div class="slot-placeholder" onclick="quickBookAppointment('${time}', '${staff.id}')">+</div>`;
                }
                
                html += '</div>';
            });
            
            html += '</div>';
        });

        html += '</div>';
        calendarContainer.innerHTML = html;
    }

    renderWeekView() {
        // Week view implementation
        console.log('Week view rendering not yet implemented');
    }

    createDayViewContainer() {
        const existingTable = document.querySelector('.table-responsive');
        if (existingTable) {
            const container = document.createElement('div');
            container.id = 'dayViewContainer';
            container.className = 'calendar-container';
            existingTable.parentNode.insertBefore(container, existingTable);
            
            // Add view switcher
            const viewSwitcher = document.createElement('div');
            viewSwitcher.className = 'view-switcher mb-3';
            viewSwitcher.innerHTML = `
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-sm btn-outline-primary active" onclick="switchCalendarView('day')">Day</button>
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="switchCalendarView('week')">Week</button>
                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="switchCalendarView('table')">Table</button>
                </div>
            `;
            container.parentNode.insertBefore(viewSwitcher, container);
        }
    }

    generateTimeSlots() {
        const slots = [];
        for (let hour = 9; hour <= 20; hour++) {
            for (let minute = 0; minute < 60; minute += 30) {
                const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                slots.push(timeString);
            }
        }
        return slots;
    }

    formatTime(timeString) {
        const [hour, minute] = timeString.split(':');
        const hour12 = hour > 12 ? hour - 12 : hour;
        const ampm = hour >= 12 ? 'PM' : 'AM';
        return `${hour12}:${minute} ${ampm}`;
    }

    generateStaffColor(staffId) {
        const colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b', '#858796'];
        return colors[parseInt(staffId) % colors.length];
    }

    getAppointmentAt(time, staffId) {
        return this.appointments.find(apt => 
            apt.time.includes(time.split(':')[0]) && 
            apt.staffName === this.getStaffName(staffId)
        );
    }

    getStaffName(staffId) {
        const staff = this.staff.find(s => s.id === staffId);
        return staff ? staff.name : '';
    }

    renderAppointmentBlock(appointment) {
        const statusClass = `status-${appointment.status}`;
        return `
            <div class="appointment-block ${statusClass}" 
                 data-appointment-id="${appointment.id}"
                 title="${appointment.clientName} - ${appointment.serviceName}">
                <div class="apt-client">${appointment.clientName}</div>
                <div class="apt-service">${appointment.serviceName}</div>
                <div class="apt-time">${appointment.time}</div>
            </div>
        `;
    }

    setupDragAndDrop() {
        // Enable drag and drop for appointment rescheduling
        document.addEventListener('dragstart', (e) => {
            if (e.target.matches('.appointment-block')) {
                e.dataTransfer.setData('text/plain', e.target.dataset.appointmentId);
                e.target.classList.add('dragging');
            }
        });

        document.addEventListener('dragend', (e) => {
            if (e.target.matches('.appointment-block')) {
                e.target.classList.remove('dragging');
            }
        });

        document.addEventListener('dragover', (e) => {
            if (e.target.matches('.time-slot.available')) {
                e.preventDefault();
                e.target.classList.add('drag-over');
            }
        });

        document.addEventListener('dragleave', (e) => {
            if (e.target.matches('.time-slot')) {
                e.target.classList.remove('drag-over');
            }
        });

        document.addEventListener('drop', (e) => {
            if (e.target.matches('.time-slot.available')) {
                e.preventDefault();
                const appointmentId = e.dataTransfer.getData('text/plain');
                const newTime = e.target.dataset.time;
                const newStaff = e.target.dataset.staff;
                
                this.rescheduleAppointment(appointmentId, newTime, newStaff);
                e.target.classList.remove('drag-over');
            }
        });
    }

    rescheduleAppointment(appointmentId, newTime, newStaff) {
        const appointment = this.appointments.find(apt => apt.id === appointmentId);
        if (appointment) {
            const confirmed = confirm(`Reschedule ${appointment.clientName}'s appointment to ${this.formatTime(newTime)}?`);
            if (confirmed) {
                // In a real app, this would make an API call
                appointment.time = newTime;
                appointment.staffName = this.getStaffName(newStaff);
                this.renderAppointments();
                this.showSuccessMessage('Appointment rescheduled successfully');
            }
        }
    }

    navigateDay(direction) {
        const newDate = new Date(this.selectedDate);
        newDate.setDate(newDate.getDate() + direction);
        this.selectedDate = newDate;
        this.updateCalendarView();
        this.loadAppointments();
    }

    goToToday() {
        this.selectedDate = new Date();
        this.updateCalendarView();
        this.loadAppointments();
    }

    changeView(viewType) {
        this.currentView = viewType;
        if (viewType === 'table') {
            this.showTableView();
        } else {
            this.renderAppointments();
        }
    }

    showTableView() {
        const calendarContainer = document.getElementById('dayViewContainer');
        const tableContainer = document.querySelector('.table-responsive');
        
        if (calendarContainer && tableContainer) {
            calendarContainer.style.display = 'none';
            tableContainer.style.display = 'block';
        }
    }

    showNewAppointmentModal(time) {
        const modal = new bootstrap.Modal(document.getElementById('addAppointmentModal'));
        const timeInput = document.getElementById('appointment_date');
        
        if (timeInput) {
            const dateString = this.selectedDate.toISOString().split('T')[0];
            timeInput.value = `${dateString}T${time}`;
        }
        
        modal.show();
    }

    showAppointmentDetails(appointmentId) {
        const appointment = this.appointments.find(apt => apt.id === appointmentId);
        if (appointment) {
            // Show appointment details modal or tooltip
            this.displayAppointmentPopover(appointment);
        }
    }

    displayAppointmentPopover(appointment) {
        // Create and show a popover with appointment details
        const popoverContent = `
            <div class="appointment-details">
                <h6>${appointment.clientName}</h6>
                <p><strong>Service:</strong> ${appointment.serviceName}</p>
                <p><strong>Time:</strong> ${appointment.time}</p>
                <p><strong>Staff:</strong> ${appointment.staffName}</p>
                <p><strong>Amount:</strong> ${appointment.amount}</p>
                <p><strong>Status:</strong> <span class="badge bg-${this.getStatusClass(appointment.status)}">${appointment.status}</span></p>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="editAppointment('${appointment.id}')">Edit</button>
                    <button class="btn btn-sm btn-success" onclick="markCompleted('${appointment.id}')">Complete</button>
                </div>
            </div>
        `;
        
        // Show popover (simplified implementation)
        alert(`Appointment Details:\n${appointment.clientName}\n${appointment.serviceName}\n${appointment.time}`);
    }

    getStatusClass(status) {
        const statusClasses = {
            'scheduled': 'info',
            'confirmed': 'primary',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary'
        };
        return statusClasses[status] || 'secondary';
    }

    handleAppointmentSubmit(form) {
        const formData = new FormData(form);
        
        // Validate form data
        if (this.validateAppointmentForm(formData)) {
            // Submit form normally (page reload)
            form.submit();
        }
    }

    validateAppointmentForm(formData) {
        const clientId = formData.get('client_id');
        const serviceId = formData.get('service_id');
        const staffId = formData.get('staff_id');
        const appointmentDate = formData.get('appointment_date');

        if (!clientId || !serviceId || !staffId || !appointmentDate) {
            this.showErrorMessage('Please fill in all required fields');
            return false;
        }

        // Check for scheduling conflicts
        const selectedDate = new Date(appointmentDate);
        const conflicts = this.checkSchedulingConflicts(selectedDate, staffId);
        
        if (conflicts.length > 0) {
            const confirmed = confirm('There may be a scheduling conflict. Do you want to continue?');
            return confirmed;
        }

        return true;
    }

    checkSchedulingConflicts(appointmentDate, staffId) {
        // Simple conflict checking
        const conflicts = [];
        const appointmentTime = appointmentDate.toTimeString().substring(0, 5);
        
        this.appointments.forEach(appointment => {
            if (appointment.staffName === this.getStaffName(staffId)) {
                if (appointment.time.includes(appointmentTime.split(':')[0])) {
                    conflicts.push(appointment);
                }
            }
        });
        
        return conflicts;
    }

    refreshAppointments() {
        // Refresh appointment data from server
        console.log('Refreshing appointments...');
        this.loadAppointments();
    }

    showSuccessMessage(message) {
        this.showToast(message, 'success');
    }

    showErrorMessage(message) {
        this.showToast(message, 'error');
    }

    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : 'success'} toast-message`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // Fade in
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 100);
        
        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Global functions for calendar interactions
function switchCalendarView(viewType) {
    if (window.bookingCalendar) {
        window.bookingCalendar.changeView(viewType);
        
        // Update active button
        document.querySelectorAll('.view-switcher .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Show/hide appropriate containers
        const calendarContainer = document.getElementById('dayViewContainer');
        const tableContainer = document.querySelector('.table-responsive');
        
        if (viewType === 'table') {
            if (calendarContainer) calendarContainer.style.display = 'none';
            if (tableContainer) tableContainer.style.display = 'block';
        } else {
            if (calendarContainer) calendarContainer.style.display = 'block';
            if (tableContainer) tableContainer.style.display = 'none';
        }
    }
}

function quickBookAppointment(time, staffId) {
    if (window.bookingCalendar) {
        window.bookingCalendar.showNewAppointmentModal(time);
        
        // Pre-select staff if available
        const staffSelect = document.getElementById('staff_id');
        if (staffSelect && staffId) {
            staffSelect.value = staffId;
        }
    }
}

function editAppointment(appointmentId) {
    console.log('Edit appointment:', appointmentId);
    // Implementation would open edit modal with appointment data
}

function markCompleted(appointmentId) {
    if (confirm('Mark this appointment as completed?')) {
        console.log('Mark completed:', appointmentId);
        // Implementation would update appointment status
    }
}

function updateServicePrice() {
    const serviceSelect = document.getElementById('service_id');
    const amountInput = document.getElementById('amount');
    
    if (serviceSelect && amountInput) {
        const selectedOption = serviceSelect.options[serviceSelect.selectedIndex];
        
        if (selectedOption && selectedOption.text.includes('$')) {
            const priceMatch = selectedOption.text.match(/\$([0-9.]+)/);
            if (priceMatch) {
                amountInput.value = priceMatch[1];
            }
        }
    }
}

// Initialize calendar when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.table-responsive')) {
        window.bookingCalendar = new BookingCalendar();
    }
});

// CSS styles for calendar (injected dynamically)
const calendarStyles = `
<style>
.calendar-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
}

.day-calendar {
    display: flex;
    flex-direction: column;
}

.calendar-header {
    display: flex;
    background: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
}

.time-column {
    width: 80px;
    padding: 10px;
    border-right: 1px solid #dee2e6;
    text-align: center;
    font-size: 0.9em;
}

.staff-column {
    flex: 1;
    padding: 10px;
    text-align: center;
    border-right: 1px solid #dee2e6;
}

.time-row {
    display: flex;
    min-height: 60px;
    border-bottom: 1px solid #dee2e6;
}

.time-label {
    width: 80px;
    padding: 10px;
    border-right: 1px solid #dee2e6;
    text-align: center;
    font-size: 0.8em;
    color: #6c757d;
    display: flex;
    align-items: center;
    justify-content: center;
}

.time-slot {
    flex: 1;
    padding: 5px;
    border-right: 1px solid #dee2e6;
    position: relative;
    cursor: pointer;
    transition: background-color 0.2s;
}

.time-slot.available:hover {
    background-color: rgba(78, 115, 223, 0.1);
}

.time-slot.occupied {
    background-color: #f8f9fa;
}

.time-slot.drag-over {
    background-color: rgba(28, 200, 138, 0.2);
}

.slot-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #6c757d;
    font-size: 1.5em;
    transition: color 0.2s;
}

.slot-placeholder:hover {
    color: var(--bs-primary);
}

.appointment-block {
    background: linear-gradient(135deg, #4e73df, #36b9cc);
    color: white;
    padding: 8px;
    border-radius: 4px;
    font-size: 0.8em;
    cursor: pointer;
    transition: transform 0.2s;
    height: 100%;
    min-height: 50px;
    draggable: true;
}

.appointment-block:hover {
    transform: scale(1.02);
}

.appointment-block.dragging {
    opacity: 0.5;
}

.appointment-block.status-scheduled {
    background: linear-gradient(135deg, #36b9cc, #1cc88a);
}

.appointment-block.status-confirmed {
    background: linear-gradient(135deg, #4e73df, #5a5c69);
}

.appointment-block.status-in_progress {
    background: linear-gradient(135deg, #f6c23e, #fd7e14);
}

.appointment-block.status-completed {
    background: linear-gradient(135deg, #1cc88a, #28a745);
}

.appointment-block.status-cancelled {
    background: linear-gradient(135deg, #e74a3b, #dc3545);
}

.apt-client {
    font-weight: 600;
    margin-bottom: 2px;
}

.apt-service {
    font-size: 0.7em;
    opacity: 0.9;
    margin-bottom: 2px;
}

.apt-time {
    font-size: 0.7em;
    opacity: 0.8;
}

.view-switcher {
    display: flex;
    justify-content: center;
}

.toast-message {
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

@media (max-width: 768px) {
    .time-column, .time-label {
        width: 60px;
        font-size: 0.7em;
    }
    
    .staff-column {
        font-size: 0.8em;
    }
    
    .appointment-block {
        font-size: 0.7em;
        padding: 4px;
    }
}
</style>
`;

// Inject calendar styles
if (document.head) {
    document.head.insertAdjacentHTML('beforeend', calendarStyles);
}
