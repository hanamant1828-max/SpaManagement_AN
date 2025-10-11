// Appointment Context Menu Implementation
class AppointmentContextMenu {
    constructor() {
        this.contextMenu = null;
        this.currentAppointmentId = null;
        this.isInitialized = false;
        this.init();
    }

    init() {
        this.createContextMenuHTML();
        this.attachGlobalEventListeners();
        this.isInitialized = true;
        console.log('🎛️ Context menu system initialized');
    }

    createContextMenuHTML() {
        // Remove existing context menu if it exists
        const existingMenu = document.getElementById('appointment-context-menu');
        if (existingMenu) {
            existingMenu.remove();
        }

        // Create context menu HTML
        const contextMenuHTML = `
            <div id="appointment-context-menu" class="context-menu" style="display: none;">
                <div class="context-menu-header">
                    <strong id="context-menu-title">Appointment Actions</strong>
                </div>
                <div class="context-menu-divider"></div>
                <ul class="context-menu-list">
                    <li class="context-menu-item" data-action="view">
                        <i class="fas fa-eye"></i> View Details
                    </li>
                    <li class="context-menu-item" data-action="edit">
                        <i class="fas fa-edit"></i> Edit Appointment
                    </li>
                    <li class="context-menu-divider"></li>
                    <li class="context-menu-item" data-action="billing">
                        <i class="fas fa-dollar-sign"></i> Go to Billing
                    </li>
                    <li class="context-menu-item" data-action="book_new">
                        <i class="fas fa-calendar-plus"></i> Book New Appointment
                    </li>
                    <li class="context-menu-item" data-action="assign_pay">
                        <i class="fas fa-handshake"></i> Assign & Pay
                    </li>
                    <li class="context-menu-item" data-action="client_management">
                        <i class="fas fa-users"></i> View Client Management
                    </li>
                    <li class="context-menu-divider"></li>
                    <li class="context-menu-item danger" data-action="cancel">
                        <i class="fas fa-times-circle"></i> Cancel Appointment
                    </li>
                </ul>
            </div>
        `;

        // Add to body
        document.body.insertAdjacentHTML('beforeend', contextMenuHTML);
        this.contextMenu = document.getElementById('appointment-context-menu');

        // Add context menu styles if not already present
        this.addContextMenuStyles();

        // Add click handlers to menu items
        this.attachContextMenuHandlers();
    }

    addContextMenuStyles() {
        const existingStyle = document.getElementById('context-menu-styles');
        if (existingStyle) return;

        const style = document.createElement('style');
        style.id = 'context-menu-styles';
        style.textContent = `
            .context-menu {
                position: fixed;
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 10000;
                min-width: 200px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                font-size: 14px;
            }

            .context-menu-header {
                padding: 12px 16px 8px;
                font-weight: 600;
                color: #333;
                border-bottom: 1px solid #eee;
            }

            .context-menu-list {
                list-style: none;
                margin: 0;
                padding: 8px 0;
            }

            .context-menu-item {
                padding: 10px 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: background-color 0.2s;
            }

            .context-menu-item:hover {
                background-color: #f5f5f5;
            }

            .context-menu-item.danger {
                color: #dc3545;
            }

            .context-menu-item.danger:hover {
                background-color: #fff5f5;
                color: #dc3545;
            }

            .context-menu-divider {
                height: 1px;
                background-color: #eee;
                margin: 4px 0;
            }

            .context-menu-item i {
                width: 16px;
                text-align: center;
            }
        `;
        document.head.appendChild(style);
    }

    attachContextMenuHandlers() {
        const menuItems = this.contextMenu.querySelectorAll('.context-menu-item[data-action]');
        menuItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleContextMenuAction(action);
                this.hideContextMenu();
            });
        });
    }

    attachGlobalEventListeners() {
        // Hide context menu on click outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#appointment-context-menu')) {
                this.hideContextMenu();
            }
        });

        // Hide context menu on scroll
        document.addEventListener('scroll', () => {
            this.hideContextMenu();
        });

        // Hide context menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideContextMenu();
            }
        });
    }

    showContextMenu(x, y, appointmentId) {
        this.currentAppointmentId = appointmentId;

        if (!this.contextMenu) {
            console.error('Context menu not initialized, recreating...');
            this.createContextMenuHTML();
            if (!this.contextMenu) {
                console.error('Failed to create context menu');
                return;
            }
        }

        // Position the menu
        this.contextMenu.style.left = `${x}px`;
        this.contextMenu.style.top = `${y}px`;
        this.contextMenu.style.display = 'block';

        // Ensure menu stays within viewport
        this.adjustMenuPosition();

        // Update header with appointment info
        this.updateContextMenuHeader(appointmentId);

        console.log(`🎯 Context menu shown for appointment ${appointmentId} at (${x}, ${y})`);
    }

    adjustMenuPosition() {
        const menu = this.contextMenu;
        const menuRect = menu.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        // Adjust horizontal position
        if (menuRect.right > viewportWidth) {
            menu.style.left = `${viewportWidth - menuRect.width - 10}px`;
        }

        // Adjust vertical position
        if (menuRect.bottom > viewportHeight) {
            menu.style.top = `${viewportHeight - menuRect.height - 10}px`;
        }
    }

    updateContextMenuHeader(appointmentId) {
        // Find appointment data
        const appointmentElement = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
        if (appointmentElement) {
            const clientName = appointmentElement.querySelector('.appointment-client')?.textContent || 'Unknown Client';
            const serviceName = appointmentElement.querySelector('.appointment-service')?.textContent || 'Unknown Service';

            const header = this.contextMenu.querySelector('#context-menu-title');
            header.textContent = `${clientName} - ${serviceName}`;
        }
    }

    hideContextMenu() {
        if (this.contextMenu) {
            this.contextMenu.style.display = 'none';
            this.currentAppointmentId = null;
        }
    }

    handleContextMenuAction(action) {
        if (!this.currentAppointmentId) {
            console.error('No appointment ID set for context menu action');
            return;
        }

        console.log(`🎬 Context menu action: ${action} for appointment ${this.currentAppointmentId}`);

        switch (action) {
            case 'view':
                this.viewAppointment(this.currentAppointmentId);
                break;
            case 'edit':
                this.editAppointment(this.currentAppointmentId);
                break;
            case 'cancel':
                this.cancelAppointment(this.currentAppointmentId);
                break;
            case 'billing':
                this.goToBilling(this.currentAppointmentId);
                break;
            case 'book_new':
                this.bookNewAppointment(this.currentAppointmentId);
                break;
            case 'assign_pay':
                this.goToAssignAndPay(this.currentAppointmentId);
                break;
            case 'client_management':
                this.goToClientManagement(this.currentAppointmentId);
                break;
            case 'delete':
                this.deleteAppointment(this.currentAppointmentId);
                break;
            default:
                console.log(`Unknown action: ${action}`);
        }
    }

    viewAppointment(appointmentId) {
        console.log(`Viewing appointment ${appointmentId}`);

        // Fetch appointment details from API
        fetch(`/api/unaki/bookings/${appointmentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.booking) {
                    this.showAppointmentDetailsModal(data.booking);
                } else {
                    console.error('Failed to fetch appointment details:', data.error);
                    this.showToast('Failed to load appointment details: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                console.error('Error fetching appointment details:', error);
                this.showToast('Error loading appointment details. Please try again.', 'error');
            });
    }

    editAppointment(appointmentId) {
        console.log(`Editing appointment ${appointmentId}`);

        // Fetch appointment details first
        fetch(`/api/unaki/bookings/${appointmentId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.booking) {
                    this.showEditAppointmentModal(data.booking);
                } else {
                    console.error('Failed to fetch appointment details:', data.error);
                    this.showToast('Failed to load appointment details for editing: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                console.error('Error fetching appointment details for editing:', error);
                this.showToast('Error loading appointment for editing. Please try again.', 'error');
            });
    }



    cancelAppointment(appointmentId) {
        if (confirm('Are you sure you want to cancel this appointment?')) {
            console.log(`Cancelling appointment ${appointmentId}`);

            // Update status to cancelled using the Unaki API endpoint
            fetch(`/api/unaki/bookings/${appointmentId}/update-status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: 'cancelled' })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log(`✅ Appointment ${appointmentId} cancelled successfully`);
                    this.showToast('Appointment cancelled successfully', 'success');

                    // Refresh the schedule
                    setTimeout(() => {
                        if (typeof refreshSchedule === 'function') {
                            refreshSchedule();
                        } else {
                            location.reload();
                        }
                    }, 1000);
                } else {
                    console.error('Failed to cancel appointment:', data.error);
                    this.showToast('Failed to cancel appointment: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                console.error('Error cancelling appointment:', error);
                this.showToast('Error cancelling appointment. Please try again.', 'error');
            });
        }
    }

    goToBilling(appointmentId) {
        console.log(`Redirecting to integrated billing for appointment ${appointmentId}`);

        // Use the Unaki-specific API endpoint to get booking details
        fetch(`/api/unaki/bookings/${appointmentId}`)
            .then(r=>r.json())
            .then(data => {
                if (data.success && data.booking) {
                    const booking = data.booking;

                    // Try to use client_id if available, otherwise redirect to general billing
                    if (booking.client_id) {
                        // Redirect to integrated billing with customer pre-selected
                        window.location.href = `/appointment/${appointmentId}/go-to-billing`;
                    } else {
                        // No client_id, try to match by phone or name
                        console.warn('No client_id found, redirecting to general billing');
                        window.location.href = `/appointment/${appointmentId}/go-to-billing`;
                    }
                } else {
                    console.error('Failed to get booking details:', data.error);
                    this.showToast('Failed to load booking details. Please try again.', 'error');
                }
            })
            .catch(error => {
                console.error('Error getting booking details:', error);
                this.showToast('Error loading booking details. Please try again.', 'error');
            });
    }

    bookNewAppointment(appointmentId) {
        console.log(`Opening booking page from appointment ${appointmentId}`);

        // Fetch appointment details to pre-fill customer info
        fetch(`/api/unaki/bookings/${appointmentId}`)
            .then(r=>r.json())
            .then(data => {
                if (data.success && data.booking) {
                    const booking = data.booking;
                    // Redirect to booking page with customer pre-selected
                    if (booking.client_id) {
                        window.location.href = `/unaki-booking?customer_id=${booking.client_id}`;
                    } else {
                        window.location.href = `/unaki-booking`;
                    }
                } else {
                    window.location.href = `/unaki-booking`;
                }
            })
            .catch(error => {
                console.error('Error loading booking page:', error);
                window.location.href = `/unaki-booking`;
            });
    }

    goToAssignAndPay(appointmentId) {
        console.log(`Redirecting to Assign & Pay for appointment ${appointmentId}`);

        // Fetch appointment details to get customer ID
        fetch(`/api/unaki/bookings/${appointmentId}`)
            .then(r=>r.json())
            .then(data => {
                if (data.success && data.booking) {
                    const booking = data.booking;
                    if (booking.client_id) {
                        // Redirect to assign packages page with customer pre-selected
                        window.location.href = `/packages/assign?customer_id=${booking.client_id}`;
                    } else {
                        this.showToast('Customer information not available. Please assign from packages page.', 'warning');
                        window.location.href = `/packages/assign`;
                    }
                } else {
                    this.showToast('Failed to load appointment details.', 'error');
                    window.location.href = `/packages/assign`;
                }
            })
            .catch(error => {
                console.error('Error loading assign & pay:', error);
                this.showToast('Error loading assign & pay page.', 'error');
                window.location.href = `/packages/assign`;
            });
    }

    goToClientManagement(appointmentId) {
        console.log(`Redirecting to Client Management for appointment ${appointmentId}`);

        // Fetch appointment details to get customer ID
        fetch(`/api/unaki/bookings/${appointmentId}`)
            .then(r=>r.json())
            .then(data => {
                if (data.success && data.booking) {
                    const booking = data.booking;
                    if (booking.client_id) {
                        // Redirect to customers page with customer highlighted
                        window.location.href = `/clients?customer_id=${booking.client_id}`;
                    } else {
                        this.showToast('Customer information not available.', 'warning');
                        window.location.href = `/clients`;
                    }
                } else {
                    this.showToast('Failed to load appointment details.', 'error');
                    window.location.href = `/clients`;
                }
            })
            .catch(error => {
                console.error('Error loading client management:', error);
                this.showToast('Error loading client management page.', 'error');
                window.location.href = `/clients`;
            });
    }

    deleteAppointment(appointmentId) {
        if (confirm('Are you sure you want to delete this appointment? This action cannot be undone.')) {
            // Make API call to delete appointment using correct endpoint
            fetch(`/api/unaki/bookings/${appointmentId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    console.log('✅ Appointment deleted successfully');
                    // Remove from DOM
                    const appointmentElement = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
                    if (appointmentElement) {
                        appointmentElement.remove();
                    }
                    // Show success message
                    if (typeof showNotification === 'function') {
                        showNotification('Appointment deleted successfully', 'success');
                    }
                    // Refresh schedule
                    if (typeof refreshSchedule === 'function') {
                        refreshSchedule();
                    }
                } else {
                    console.error('Failed to delete appointment:', data.error);
                    this.showToast('Failed to delete appointment: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error deleting appointment:', error);
                this.showToast('Error deleting appointment. Please try again.', 'error');
            });
        }
    }

    updateAppointmentStatus(appointmentId, status) {
        fetch(`/api/unaki/bookings/${appointmentId}/update-status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: status })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log(`✅ Appointment ${appointmentId} status updated to ${status}`);

                // Update visual indication
                const appointmentElement = document.querySelector(`[data-appointment-id="${appointmentId}"]`);
                if (appointmentElement) {
                    appointmentElement.classList.add(`status-${status}`);

                    // If cancelled, add visual styling
                    if (status === 'cancelled') {
                        appointmentElement.style.opacity = '0.6';
                        appointmentElement.style.textDecoration = 'line-through';
                    }
                }

                // Show success message
                this.showToast(`Appointment marked as ${status}`, 'success');

                // Refresh schedule after short delay
                setTimeout(() => {
                    if (typeof refreshSchedule === 'function') {
                        refreshSchedule();
                    } else {
                        location.reload();
                    }
                }, 1000);
            } else {
                console.error(`Failed to update appointment status:`, data.error);
                this.showToast(`Failed to update appointment status: ${data.error || 'Unknown error'}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error updating appointment status:', error);
            this.showToast('Error updating appointment status. Please try again.', 'error');
        });
    }

    showAppointmentDetailsModal(appointment) {
        console.log('📋 Showing appointment details modal:', appointment);

        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="appointmentDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-primary text-white">
                            <h5 class="modal-title">
                                <i class="fas fa-eye me-2"></i>Appointment Details
                            </h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="fw-bold text-primary mb-3">Client Information</h6>
                                    <div class="mb-2">
                                        <strong>Name:</strong> ${appointment.client_name || 'N/A'}
                                    </div>
                                    <div class="mb-2">
                                        <strong>Phone:</strong> ${appointment.client_phone || 'N/A'}
                                    </div>
                                    <div class="mb-2">
                                        <strong>Email:</strong> ${appointment.client_email || 'N/A'}
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="fw-bold text-success mb-3">Service Information</h6>
                                    <div class="mb-2">
                                        <strong>Service:</strong> ${appointment.service_name || 'N/A'}
                                    </div>
                                    <div class="mb-2">
                                        <strong>Duration:</strong> ${appointment.service_duration || 'N/A'} minutes
                                    </div>
                                </div>
                            </div>
                            <hr>
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="fw-bold text-info mb-3">Schedule Information</h6>
                                    <div class="mb-2">
                                        <strong>Date:</strong> ${new Date(appointment.appointment_date).toLocaleDateString()}
                                    </div>
                                    <div class="mb-2">
                                        <strong>Time:</strong> ${appointment.start_time} - ${appointment.end_time}
                                    </div>
                                    <div class="mb-2">
                                        <strong>Staff:</strong> ${appointment.staff_name || 'N/A'}
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="fw-bold text-warning mb-3">Status & Payment</h6>
                                    <div class="mb-2">
                                        <strong>Status:</strong> 
                                        <span class="badge bg-${this.getStatusBadgeClass(appointment.status)}">${appointment.status || 'scheduled'}</span>
                                    </div>
                                    <div class="mb-2">
                                        <strong>Payment:</strong> 
                                        <span class="badge bg-${this.getPaymentBadgeClass(appointment.payment_status)}">${appointment.payment_status || 'pending'}</span>
                                    </div>
                                </div>
                            </div>
                            ${appointment.notes ? `
                                <hr>
                                <div class="row">
                                    <div class="col-12">
                                        <h6 class="fw-bold text-secondary mb-3">Notes</h6>
                                        <div class="bg-light p-3 rounded">${appointment.notes}</div>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-outline-primary" onclick="appointmentContextMenu.editAppointment(${appointment.id})">
                                <i class="fas fa-edit me-1"></i>Edit
                            </button>
                            <button type="button" class="btn btn-outline-success" onclick="appointmentContextMenu.goToBilling(${appointment.id})">
                                <i class="fas fa-dollar-sign me-1"></i>Billing
                            </button>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('appointmentDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to document
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('appointmentDetailsModal'));
        modal.show();
    }

    showEditAppointmentModal(appointment) {
        console.log('✏️ Showing edit appointment modal:', appointment);

        // Create edit modal HTML
        const modalHTML = `
            <div class="modal fade" id="editAppointmentModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header bg-warning text-dark">
                            <h5 class="modal-title">
                                <i class="fas fa-edit me-2"></i>Edit Appointment
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <form id="editAppointmentForm">
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="fw-bold text-primary mb-3">Client Information</h6>
                                        <div class="mb-3">
                                            <label for="editClientName" class="form-label">Client Name *</label>
                                            <input type="text" class="form-control" id="editClientName" value="${appointment.client_name || ''}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="editClientPhone" class="form-label">Phone</label>
                                            <input type="tel" class="form-control" id="editClientPhone" value="${appointment.client_phone || ''}">
                                        </div>
                                        <div class="mb-3">
                                            <label for="editClientEmail" class="form-label">Email</label>
                                            <input type="email" class="form-control" id="editClientEmail" value="${appointment.client_email || ''}">
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="fw-bold text-success mb-3">Service Information</h6>
                                        <div class="mb-3">
                                            <label for="editServiceName" class="form-label">Service *</label>
                                            <input type="text" class="form-control" id="editServiceName" value="${appointment.service_name || ''}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="editServiceDuration" class="form-label">Duration (minutes)</label>
                                            <input type="number" class="form-control" id="editServiceDuration" value="${appointment.service_duration || 60}" min="5" max="480">
                                        </div>
                                        <div class="mb-3">
                                            <label for="editServicePrice" class="form-label">Price (₹)</label>
                                            <input type="number" class="form-control" id="editServicePrice" value="${appointment.service_price || 0}" min="0" step="0.01">
                                        </div>
                                        <div class="mb-3">
                                            <label for="editStaffId" class="form-label">Assigned Staff *</label>
                                            <input type="number" class="form-control" id="editStaffId" value="${appointment.staff_id || ''}" required readonly style="display: none;">
                                            <input type="text" class="form-control" value="${appointment.staff_name || 'Staff Member'}" readonly>
                                            <small class="text-muted">Staff ID: ${appointment.staff_id || 'N/A'}</small>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6 class="fw-bold text-info mb-3">Schedule Information</h6>
                                        <div class="mb-3">
                                            <label for="editAppointmentDate" class="form-label">Date *</label>
                                            <input type="date" class="form-control" id="editAppointmentDate" value="${appointment.appointment_date}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="editStartTime" class="form-label">Start Time *</label>
                                            <input type="time" class="form-control" id="editStartTime" value="${appointment.start_time}" required>
                                        </div>
                                        <div class="mb-3">
                                            <label for="editEndTime" class="form-label">End Time *</label>
                                            <input type="time" class="form-control" id="editEndTime" value="${appointment.end_time}" required>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6 class="fw-bold text-warning mb-3">Status & Notes</h6>
                                        <div class="mb-3">
                                            <label for="editStatus" class="form-label">Status</label>
                                            <select class="form-control" id="editStatus">
                                                <option value="scheduled" ${appointment.status === 'scheduled' ? 'selected' : ''}>Scheduled</option>
                                                <option value="confirmed" ${appointment.status === 'confirmed' ? 'selected' : ''}>Confirmed</option>
                                                <option value="in_progress" ${appointment.status === 'in_progress' ? 'selected' : ''}>In Progress</option>
                                                <option value="completed" ${appointment.status === 'completed' ? 'selected' : ''}>Completed</option>
                                                <option value="cancelled" ${appointment.status === 'cancelled' ? 'selected' : ''}>Cancelled</option>
                                                <option value="no_show" ${appointment.status === 'no_show' ? 'selected' : ''}>No Show</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label for="editPaymentStatus" class="form-label">Payment Status</label>
                                            <select class="form-control" id="editPaymentStatus">
                                                <option value="pending" ${appointment.payment_status === 'pending' ? 'selected' : ''}>Pending</option>
                                                <option value="paid" ${appointment.payment_status === 'paid' ? 'selected' : ''}>Paid</option>
                                                <option value="partial" ${appointment.payment_status === 'partial' ? 'selected' : ''}>Partial</option>
                                                <option value="refunded" ${appointment.payment_status === 'refunded' ? 'selected' : ''}>Refunded</option>
                                            </select>
                                        </div>
                                        <div class="mb-3">
                                            <label for="editNotes" class="form-label">Notes</label>
                                            <textarea class="form-control" id="editNotes" rows="3">${appointment.notes || ''}</textarea>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-primary">
                                    <i class="fas fa-save me-1"></i>Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('editAppointmentModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to document
        document.body.insertAdjacentHTML('beforeend', modalHTML);

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('editAppointmentModal'));
        modal.show();

        // Add form submit handler
        document.getElementById('editAppointmentForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveAppointmentChanges(appointment.id, modal);
        });
    }

    saveAppointmentChanges(appointmentId, modal) {
        console.log(`💾 Saving changes for appointment ${appointmentId}`);

        // Collect form data
        const formData = {
            client_name: document.getElementById('editClientName').value,
            client_phone: document.getElementById('editClientPhone').value,
            client_email: document.getElementById('editClientEmail').value,
            service_name: document.getElementById('editServiceName').value,
            service_duration: parseInt(document.getElementById('editServiceDuration').value),
            service_price: parseFloat(document.getElementById('editServicePrice').value),
            staff_id: parseInt(document.getElementById('editStaffId').value),
            appointment_date: document.getElementById('editAppointmentDate').value,
            start_time: document.getElementById('editStartTime').value,
            end_time: document.getElementById('editEndTime').value,
            status: document.getElementById('editStatus').value,
            payment_status: document.getElementById('editPaymentStatus').value,
            notes: document.getElementById('editNotes').value
        };

        // Send update request
        fetch(`/api/unaki/bookings/${appointmentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('✅ Appointment updated successfully');
                modal.hide();

                // Show success message
                if (typeof showNotification === 'function') {
                    showNotification('Appointment updated successfully', 'success');
                } else {
                    this.showToast('Appointment updated successfully!', 'success');
                }

                // Refresh schedule
                if (typeof refreshSchedule === 'function') {
                    refreshSchedule();
                } else if (typeof location !== 'undefined') {
                    location.reload();
                }
            } else {
                console.error('Failed to update appointment:', data.error);
                this.showToast('Failed to update appointment: ' + (data.error || 'Unknown error'), 'error');
            }
        })
        .catch(error => {
            console.error('Error updating appointment:', error);
            this.showToast('Error updating appointment. Please try again.', 'error');
        });
    }

    getStatusBadgeClass(status) {
        const statusClasses = {
            'scheduled': 'primary',
            'confirmed': 'info',
            'in_progress': 'warning',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'secondary'
        };
        return statusClasses[status] || 'secondary';
    }

    getPaymentBadgeClass(paymentStatus) {
        const paymentClasses = {
            'pending': 'warning',
            'paid': 'success',
            'partial': 'info',
            'refunded': 'danger'
        };
        return paymentClasses[paymentStatus] || 'secondary';
    }

    // Utility method to safely escape HTML and prevent XSS
    escapeHtml(text) {
        if (typeof text !== 'string') return text;
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Show toast notifications instead of alert dialogs
    showToast(message, type = 'info') {
        // Remove any existing toasts first
        const existingToasts = document.querySelectorAll('.custom-toast');
        existingToasts.forEach(toast => toast.remove());

        // Create toast element
        const toast = document.createElement('div');
        toast.className = `custom-toast toast-${type}`;

        // Set toast styles
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getToastColor(type)};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            z-index: 10000;
            font-weight: 500;
            font-size: 14px;
            max-width: 350px;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        `;

        // Escape the message to prevent XSS
        toast.textContent = message;

        // Add icon
        const icon = document.createElement('i');
        icon.className = this.getToastIcon(type);
        icon.style.marginRight = '8px';
        toast.prepend(icon);

        // Add to document
        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Auto-remove after delay
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, type === 'error' ? 5000 : 3000); // Error messages stay longer
    }

    getToastColor(type) {
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#17a2b8'
        };
        return colors[type] || colors.info;
    }

    getToastIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    reinitializeForAppointments() {
        // This function is called after DOM updates to reattach event listeners
        console.log('🔄 Reinitializing context menu for appointments');

        // Find all appointment blocks
        const appointmentBlocks = document.querySelectorAll('.appointment-block');
        console.log(`🔍 Found ${appointmentBlocks.length} appointment blocks to initialize`);

        appointmentBlocks.forEach((block, index) => {
            // Remove existing right-click listeners
            const clone = block.cloneNode(true);
            block.parentNode.replaceChild(clone, block);

            // Add right-click event listener for desktop
            clone.addEventListener('contextmenu', (event) => {
                event.preventDefault();
                event.stopPropagation();

                const appointmentId = this.getAppointmentId(clone);
                if (appointmentId) {
                    console.log(`🎯 Right-click detected on appointment ${appointmentId}`);
                    this.showContextMenu(event.pageX, event.pageY, appointmentId);
                } else {
                    console.error('No appointment ID found for right-clicked element');
                }
            });

            // Add mobile touch support
            let touchTimer = null;
            let touchStartX = 0;
            let touchStartY = 0;
            let longPressTriggered = false;

            clone.addEventListener('touchstart', (event) => {
                touchStartX = event.touches[0].clientX;
                touchStartY = event.touches[0].clientY;
                longPressTriggered = false;

                // Visual feedback for long press
                clone.style.transform = 'scale(0.98)';
                clone.style.opacity = '0.8';

                // Long press detection
                touchTimer = setTimeout(() => {
                    const appointmentId = this.getAppointmentId(clone);
                    if (appointmentId) {
                        longPressTriggered = true;
                        console.log(`📱 Long press detected on appointment ${appointmentId}`);

                        // Add vibration feedback if available
                        if (navigator.vibrate) {
                            navigator.vibrate(50);
                        }

                        // Reset visual feedback
                        clone.style.transform = '';
                        clone.style.opacity = '';

                        this.showContextMenu(touchStartX, touchStartY, appointmentId);
                    }
                }, 500); // 500ms long press
            });

            clone.addEventListener('touchmove', (event) => {
                // Cancel long press if finger moves too much
                const moveX = Math.abs(event.touches[0].clientX - touchStartX);
                const moveY = Math.abs(event.touches[0].clientY - touchStartY);
                if (moveX > 10 || moveY > 10) {
                    clearTimeout(touchTimer);
                    clone.style.transform = '';
                    clone.style.opacity = '';
                }
            });

            clone.addEventListener('touchend', (event) => {
                clearTimeout(touchTimer);
                clone.style.transform = '';
                clone.style.opacity = '';

                // Prevent click event if long press was triggered
                if (longPressTriggered) {
                    event.preventDefault();
                    event.stopPropagation();
                }
            });

            // Add quick tap to edit directly (mobile-friendly)
            clone.addEventListener('click', (event) => {
                const appointmentId = this.getAppointmentId(clone);
                if (appointmentId) {
                    console.log(`📱 Tap to edit appointment ${appointmentId}`);
                    event.preventDefault();
                    event.stopPropagation();
                    this.editAppointment(appointmentId);
                }
            });

            // Mark as context menu ready
            clone.setAttribute('data-context-menu-ready', 'true');
            console.log(`✅ Context menu attached to appointment ${index + 1}: ID ${this.getAppointmentId(clone)}`);
        });

        console.log('✅ Context menu reinitialized');
        console.log(`📊 Context menu coverage: ${appointmentBlocks.length}/${appointmentBlocks.length} appointment blocks`);
    }

    getAppointmentId(element) {
        // Try multiple ways to get appointment ID
        return element.dataset.appointmentId || 
               element.getAttribute('data-appointment-id') || 
               element.getAttribute('data-id') ||
               null;
    }
}

// Global instance
let appointmentContextMenu = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    appointmentContextMenu = new AppointmentContextMenu();

    // Make sure it's available globally
    window.appointmentContextMenu = appointmentContextMenu;
});

// Global functions for compatibility
window.reinitializeContextMenu = function() {
    if (window.appointmentContextMenu) {
        window.appointmentContextMenu.reinitializeForAppointments();
    } else if (appointmentContextMenu) {
        appointmentContextMenu.reinitializeForAppointments();
    } else {
        console.error('Context menu not initialized yet');
        // Try to initialize it
        setTimeout(() => {
            if (typeof AppointmentContextMenu !== 'undefined') {
                window.appointmentContextMenu = new AppointmentContextMenu();
                window.appointmentContextMenu.reinitializeForAppointments();
            }
        }, 100);
    }
};

window.handleAppointmentRightClick = function(event) {
    const contextMenu = window.appointmentContextMenu || appointmentContextMenu;

    if (contextMenu) {
        event.preventDefault();
        event.stopPropagation();

        const appointmentElement = event.currentTarget;
        const appointmentId = contextMenu.getAppointmentId(appointmentElement);

        if (appointmentId) {
            console.log(`🎯 Right-click detected on appointment ${appointmentId}`);
            contextMenu.showContextMenu(event.pageX, event.pageY, appointmentId);
        } else {
            console.error('No appointment ID found for right-clicked element');
        }
    } else {
        console.error('Context menu not available');
        // Fallback
        const appointmentElement = event.currentTarget;
        const appointmentId = appointmentElement.dataset.appointmentId || appointmentElement.getAttribute('data-appointment-id');
        if (appointmentId && typeof showFallbackContextMenu === 'function') {
            showFallbackContextMenu(event, appointmentId);
        }
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { AppointmentContextMenu };
}