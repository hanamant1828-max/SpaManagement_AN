/**
 * Flexible Schedule System with Dynamic Time Slots
 * Supports variable appointment durations and click-and-drag booking
 */

class FlexibleScheduler {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            startHour: options.startHour || 8,   // 8 AM
            endHour: options.endHour || 18,      // 6 PM
            timeInterval: options.timeInterval || 15, // 15-minute intervals
            pixelsPerHour: options.pixelsPerHour || 80, // 80px per hour to match CSS
            ...options
        };
        
        this.staffMembers = [];
        this.appointments = [];
        this.breaks = [];
        this.isDragging = false;
        this.dragStart = null;
        this.currentDrag = null;
        
        this.init();
    }
    
    init() {
        this.setupContainer();
        this.createTimeGrid();
        this.setupEventListeners();
    }
    
    setupContainer() {
        this.container.className = 'flexible-schedule-container';
        this.container.innerHTML = `
            <div class="schedule-header">
                <div class="time-column-header">Staff</div>
                <div class="staff-columns-header" id="staffHeader"></div>
            </div>
            <div class="schedule-content">
                <div class="time-column" id="timeColumn"></div>
                <div class="schedule-grid" id="scheduleGrid"></div>
            </div>
        `;
    }
    
    createTimeGrid() {
        const timeColumn = this.container.querySelector('#timeColumn');
        const scheduleGrid = this.container.querySelector('#scheduleGrid');
        
        // Clear existing content
        timeColumn.innerHTML = '';
        scheduleGrid.innerHTML = '';
        
        // Generate time labels (every hour)
        const totalHours = this.options.endHour - this.options.startHour;
        for (let hour = 0; hour <= totalHours; hour++) {
            const currentHour = this.options.startHour + hour;
            const timeLabel = document.createElement('div');
            timeLabel.className = 'time-label';
            timeLabel.style.top = `${hour * this.options.pixelsPerHour}px`;
            timeLabel.textContent = this.formatHour(currentHour);
            timeColumn.appendChild(timeLabel);
        }
        
        // Set container height
        const totalHeight = totalHours * this.options.pixelsPerHour;
        scheduleGrid.style.height = `${totalHeight}px`;
        timeColumn.style.height = `${totalHeight}px`;
    }
    
    setupEventListeners() {
        const scheduleGrid = this.container.querySelector('#scheduleGrid');
        
        scheduleGrid.addEventListener('mousedown', (e) => this.handleMouseDown(e));
        scheduleGrid.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        scheduleGrid.addEventListener('mouseup', (e) => this.handleMouseUp(e));
        scheduleGrid.addEventListener('mouseleave', (e) => this.handleMouseUp(e));
        
        // Prevent text selection during drag
        scheduleGrid.addEventListener('selectstart', (e) => e.preventDefault());
    }
    
    setStaffMembers(staffMembers) {
        this.staffMembers = staffMembers;
        this.renderStaffColumns();
    }
    
    setAppointments(appointments) {
        this.appointments = appointments;
        this.renderAppointments();
    }
    
    setBreaks(breaks) {
        this.breaks = breaks;
        this.renderBreaks();
    }
    
    renderStaffColumns() {
        const staffHeader = this.container.querySelector('#staffHeader');
        const scheduleGrid = this.container.querySelector('#scheduleGrid');
        
        staffHeader.innerHTML = '';
        scheduleGrid.style.gridTemplateColumns = `repeat(${this.staffMembers.length}, 1fr)`;
        
        this.staffMembers.forEach((staff, index) => {
            // Header
            const headerColumn = document.createElement('div');
            headerColumn.className = 'staff-header-column';
            headerColumn.innerHTML = `
                <div class="staff-name">${staff.first_name} ${staff.last_name}</div>
                <div class="staff-role">${staff.role}</div>
                <div class="staff-shift">${this.getShiftDisplay(staff)}</div>
            `;
            staffHeader.appendChild(headerColumn);
            
            // Grid column
            const gridColumn = document.createElement('div');
            gridColumn.className = 'staff-grid-column';
            gridColumn.dataset.staffId = staff.id;
            gridColumn.dataset.columnIndex = index;
            scheduleGrid.appendChild(gridColumn);
        });
    }
    
    renderAppointments() {
        // Clear existing appointments
        this.container.querySelectorAll('.appointment-block').forEach(el => el.remove());
        
        this.appointments.forEach(appointment => {
            this.renderAppointmentBlock(appointment);
        });
    }
    
    renderAppointmentBlock(appointment) {
        const staffColumn = this.container.querySelector(`[data-staff-id="${appointment.staff_id}"]`);
        if (!staffColumn) return;
        
        const block = document.createElement('div');
        block.className = 'appointment-block';
        block.dataset.appointmentId = appointment.id;
        
        const { top, height } = this.calculateBlockPosition(appointment.start_time, appointment.end_time);
        
        block.style.top = `${top}px`;
        block.style.height = `${height}px`;
        block.style.left = '2px';
        block.style.right = '2px';
        block.style.position = 'absolute';
        
        // Create elements safely to prevent XSS
        const clientDiv = document.createElement('div');
        clientDiv.className = 'appointment-client';
        clientDiv.textContent = appointment.client_name;
        
        const serviceDiv = document.createElement('div');
        serviceDiv.className = 'appointment-service';
        serviceDiv.textContent = appointment.service_name;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'appointment-time';
        timeDiv.textContent = `${this.formatTime(appointment.start_time)} - ${this.formatTime(appointment.end_time)}`;
        
        block.appendChild(clientDiv);
        block.appendChild(serviceDiv);
        block.appendChild(timeDiv);
        
        block.addEventListener('click', () => this.showAppointmentDetails(appointment));
        
        staffColumn.appendChild(block);
    }
    
    renderBreaks() {
        // Clear existing breaks
        this.container.querySelectorAll('.break-block').forEach(el => el.remove());
        
        this.breaks.forEach(breakItem => {
            this.renderBreakBlock(breakItem);
        });
    }
    
    renderBreakBlock(breakItem) {
        const staffColumn = this.container.querySelector(`[data-staff-id="${breakItem.staff_id}"]`);
        if (!staffColumn) return;
        
        const block = document.createElement('div');
        block.className = 'break-block';
        
        const { top, height } = this.calculateBlockPosition(breakItem.start_time, breakItem.end_time);
        
        block.style.top = `${top}px`;
        block.style.height = `${height}px`;
        block.style.left = '2px';
        block.style.right = '2px';
        block.style.position = 'absolute';
        
        // Create elements safely to prevent XSS
        const iconDiv = document.createElement('div');
        iconDiv.className = 'break-icon';
        iconDiv.innerHTML = '<i class="fas fa-coffee"></i>';
        
        const labelDiv = document.createElement('div');
        labelDiv.className = 'break-label';
        labelDiv.textContent = 'Break';
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'break-time';
        timeDiv.textContent = `${this.formatTime(breakItem.start_time)} - ${this.formatTime(breakItem.end_time)}`;
        
        block.appendChild(iconDiv);
        block.appendChild(labelDiv);
        block.appendChild(timeDiv);
        
        staffColumn.appendChild(block);
    }
    
    calculateBlockPosition(startTime, endTime) {
        const start = this.parseTime(startTime);
        const end = this.parseTime(endTime);
        
        const startMinutes = (start.hour - this.options.startHour) * 60 + start.minute;
        const duration = (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute);
        
        const top = (startMinutes / 60) * this.options.pixelsPerHour;
        const height = (duration / 60) * this.options.pixelsPerHour;
        
        return { top, height };
    }
    
    handleMouseDown(e) {
        const staffColumn = e.target.closest('.staff-grid-column');
        if (!staffColumn) return;
        
        // Don't start drag if clicking on existing appointment or break
        if (e.target.closest('.appointment-block, .break-block')) return;
        
        this.isDragging = true;
        this.container.classList.add('dragging');
        const rect = staffColumn.getBoundingClientRect();
        const y = e.clientY - rect.top;
        
        this.dragStart = {
            staffId: staffColumn.dataset.staffId,
            staffName: this.getStaffName(staffColumn.dataset.staffId),
            columnIndex: staffColumn.dataset.columnIndex,
            y: y,
            startTime: this.pixelsToTime(y)
        };
        
        // Create drag indicator
        this.currentDrag = document.createElement('div');
        this.currentDrag.className = 'drag-indicator';
        this.currentDrag.style.position = 'absolute';
        this.currentDrag.style.left = '2px';
        this.currentDrag.style.right = '2px';
        this.currentDrag.style.top = `${y}px`;
        this.currentDrag.style.height = '0px';
        staffColumn.appendChild(this.currentDrag);
        
        e.preventDefault();
    }
    
    handleMouseMove(e) {
        if (!this.isDragging || !this.currentDrag) return;
        
        const staffColumn = e.target.closest('.staff-grid-column') || 
                           this.container.querySelector(`[data-column-index="${this.dragStart.columnIndex}"]`);
        if (!staffColumn) return;
        
        const rect = staffColumn.getBoundingClientRect();
        const currentY = e.clientY - rect.top;
        
        const startY = Math.min(this.dragStart.y, currentY);
        const height = Math.abs(currentY - this.dragStart.y);
        
        this.currentDrag.style.top = `${startY}px`;
        this.currentDrag.style.height = `${height}px`;
        
        // Update drag info
        const endTime = this.pixelsToTime(currentY);
        this.currentDrag.title = `${this.dragStart.staffName}: ${this.dragStart.startTime} - ${endTime}`;
    }
    
    handleMouseUp(e) {
        if (!this.isDragging) return;
        
        this.isDragging = false;
        this.container.classList.remove('dragging');
        
        if (this.currentDrag) {
            const staffColumn = this.container.querySelector(`[data-column-index="${this.dragStart.columnIndex}"]`);
            const rect = staffColumn.getBoundingClientRect();
            const endY = e.clientY - rect.top;
            const endTime = this.pixelsToTime(endY);
            
            // Only create appointment if minimum duration (15 minutes)
            const duration = this.getTimeDifferenceMinutes(this.dragStart.startTime, endTime);
            if (Math.abs(duration) >= 15) {
                const bookingData = {
                    staffId: this.dragStart.staffId,
                    staffName: this.dragStart.staffName,
                    startTime: duration > 0 ? this.dragStart.startTime : endTime,
                    endTime: duration > 0 ? endTime : this.dragStart.startTime
                };
                
                // Basic collision check
                if (this.checkForConflicts(bookingData)) {
                    alert('This time slot conflicts with an existing appointment or break. Please choose a different time.');
                    return;
                }
                
                this.openBookingModal(bookingData);
            }
            
            this.currentDrag.remove();
            this.currentDrag = null;
        }
        
        this.dragStart = null;
    }
    
    // Helper methods
    parseTime(timeString) {
        const [hour, minute] = timeString.split(':').map(Number);
        return { hour, minute };
    }
    
    formatHour(hour) {
        if (hour === 0) return '12:00 AM';
        if (hour === 12) return '12:00 PM';
        return hour < 12 ? `${hour}:00 AM` : `${hour - 12}:00 PM`;
    }
    
    formatTime(timeString) {
        const { hour, minute } = this.parseTime(timeString);
        const period = hour < 12 ? 'AM' : 'PM';
        const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
        return `${displayHour}:${minute.toString().padStart(2, '0')} ${period}`;
    }
    
    pixelsToTime(pixels) {
        const totalMinutes = (pixels / this.options.pixelsPerHour) * 60;
        let hour = Math.floor(totalMinutes / 60) + this.options.startHour;
        let minute = Math.round((totalMinutes % 60) / this.options.timeInterval) * this.options.timeInterval;
        
        // Handle minute overflow (e.g., 60 minutes should become next hour)
        if (minute >= 60) {
            minute = 0;
            hour += 1;
        }
        
        // Clamp to schedule bounds
        if (hour < this.options.startHour) {
            hour = this.options.startHour;
            minute = 0;
        }
        if (hour >= this.options.endHour) {
            hour = this.options.endHour - 1;
            minute = 60 - this.options.timeInterval;
        }
        
        return `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
    }
    
    getTimeDifferenceMinutes(startTime, endTime) {
        const start = this.parseTime(startTime);
        const end = this.parseTime(endTime);
        return (end.hour * 60 + end.minute) - (start.hour * 60 + start.minute);
    }
    
    getStaffName(staffId) {
        const staff = this.staffMembers.find(s => s.id == staffId);
        return staff ? `${staff.first_name} ${staff.last_name}` : 'Unknown Staff';
    }
    
    getShiftDisplay(staff) {
        // This should be customized based on your shift data structure
        if (staff.shift_start && staff.shift_end) {
            return `${this.formatTime(staff.shift_start)} - ${this.formatTime(staff.shift_end)}`;
        }
        return 'Not scheduled';
    }
    
    openBookingModal(bookingData) {
        // Check if modal exists first
        const modalElement = document.getElementById('quickBookModal');
        if (!modalElement) {
            // Fallback: show alert with booking data
            alert(`New appointment request:\nStaff: ${bookingData.staffName}\nTime: ${bookingData.startTime} - ${bookingData.endTime}\n\nPlease use the Quick Book button to create appointments.`);
            return;
        }
        
        // Populate the booking modal with the drag data
        if (typeof populateBookingModal === 'function') {
            populateBookingModal(bookingData);
        }
        
        // Show the modal
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
        
        console.log('Opening booking modal:', bookingData);
    }
    
    showAppointmentDetails(appointment) {
        if (typeof showAppointmentDetails === 'function') {
            showAppointmentDetails(appointment.id);
        } else {
            console.log('Appointment details:', appointment);
        }
    }
    
    // Check for conflicts with existing appointments and breaks
    checkForConflicts(bookingData) {
        const startMinutes = this.timeToMinutes(bookingData.startTime);
        const endMinutes = this.timeToMinutes(bookingData.endTime);
        
        // Check against appointments
        for (const appointment of this.appointments) {
            if (appointment.staff_id == bookingData.staffId) {
                const apptStart = this.timeToMinutes(appointment.start_time);
                const apptEnd = this.timeToMinutes(appointment.end_time);
                
                if ((startMinutes < apptEnd && endMinutes > apptStart)) {
                    return true; // Conflict found
                }
            }
        }
        
        // Check against breaks
        for (const breakItem of this.breaks) {
            if (breakItem.staff_id == bookingData.staffId) {
                const breakStart = this.timeToMinutes(breakItem.start_time);
                const breakEnd = this.timeToMinutes(breakItem.end_time);
                
                if ((startMinutes < breakEnd && endMinutes > breakStart)) {
                    return true; // Conflict found
                }
            }
        }
        
        return false; // No conflicts
    }
    
    // Helper to convert time string to minutes
    timeToMinutes(timeString) {
        const [hours, minutes] = timeString.split(':').map(Number);
        return hours * 60 + minutes;
    }
}

// Global function to populate booking modal
function populateBookingModal(bookingData) {
    // Set hidden fields
    const staffInput = document.getElementById('selectedStaffId');
    const timeInput = document.getElementById('selectedTime');
    const endTimeInput = document.getElementById('selectedEndTime');
    const staffNameInput = document.getElementById('selectedStaffName');
    const timeDisplayInput = document.getElementById('selectedTimeDisplay');
    
    if (staffInput) {
        staffInput.value = bookingData.staffId;
    }
    if (timeInput) {
        timeInput.value = bookingData.startTime;
    }
    if (endTimeInput) {
        endTimeInput.value = bookingData.endTime;
    }
    if (staffNameInput) {
        staffNameInput.value = bookingData.staffName;
    }
    if (timeDisplayInput) {
        timeDisplayInput.value = `${bookingData.startTime} - ${bookingData.endTime}`;
    }
    
    // Update modal title
    const modalTitle = document.querySelector('#quickBookModal .modal-title');
    if (modalTitle) {
        modalTitle.innerHTML = `<i class="fas fa-plus me-2"></i>Book Appointment - ${bookingData.staffName}`;
    }
    
    // Show selected time info
    const timeInfo = document.getElementById('selected-time-info');
    if (timeInfo) {
        timeInfo.innerHTML = `
            <strong>Selected Time:</strong> ${bookingData.startTime} - ${bookingData.endTime}<br>
            <strong>Staff:</strong> ${bookingData.staffName}
        `;
        timeInfo.style.display = 'block';
    }
}

// Initialize scheduler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const scheduleContainer = document.getElementById('flexibleScheduleContainer');
    if (scheduleContainer && typeof window.staffScheduleData !== 'undefined') {
        window.scheduler = new FlexibleScheduler(scheduleContainer, {
            startHour: 8,
            endHour: 18,
            pixelsPerHour: 80
        });
        
        // Load data if available
        if (window.staffScheduleData.staff) {
            window.scheduler.setStaffMembers(window.staffScheduleData.staff);
        }
        if (window.staffScheduleData.appointments) {
            window.scheduler.setAppointments(window.staffScheduleData.appointments);
        }
        if (window.staffScheduleData.breaks) {
            window.scheduler.setBreaks(window.staffScheduleData.breaks);
        }
    }
});