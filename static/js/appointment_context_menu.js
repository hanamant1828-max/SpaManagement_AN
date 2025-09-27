/**
 * Appointment Context Menu for Right-Click "Go to Integrated Billing"
 * Works with all booking templates and appointment blocks
 */

class AppointmentContextMenu {
    constructor() {
        this.contextMenu = null;
        this.currentAppointmentId = null;
        this.init();
    }

    init() {
        this.createContextMenu();
        this.setupEventListeners();
    }

    createContextMenu() {
        // Create context menu HTML
        this.contextMenu = document.createElement('div');
        this.contextMenu.id = 'appointment-context-menu';
        this.contextMenu.className = 'appointment-context-menu';
        this.contextMenu.innerHTML = `
            <div class="context-menu-item" data-action="go-to-billing">
                <i class="fas fa-receipt me-2"></i>Go to Integrated Billing
            </div>
            <div class="context-menu-item" data-action="view-details">
                <i class="fas fa-eye me-2"></i>View Details
            </div>
            <div class="context-menu-item" data-action="edit-appointment">
                <i class="fas fa-edit me-2"></i>Edit Appointment
            </div>
        `;
        
        // Add CSS styles
        this.addContextMenuStyles();
        
        document.body.appendChild(this.contextMenu);
    }

    addContextMenuStyles() {
        if (document.getElementById('appointment-context-menu-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'appointment-context-menu-styles';
        style.textContent = `
            .appointment-context-menu {
                position: fixed;
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                z-index: 9999;
                min-width: 200px;
                padding: 8px 0;
                display: none;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            
            .context-menu-item {
                padding: 10px 16px;
                cursor: pointer;
                font-size: 14px;
                color: #333;
                display: flex;
                align-items: center;
                transition: background-color 0.2s;
            }
            
            .context-menu-item:hover {
                background-color: #f5f5f5;
            }
            
            .context-menu-item[data-action="go-to-billing"]:hover {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            .appointment-block {
                cursor: pointer;
                position: relative;
            }
            
            .appointment-block:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        `;
        document.head.appendChild(style);
    }

    setupEventListeners() {
        // Right-click on appointment blocks
        document.addEventListener('contextmenu', (e) => {
            const appointmentBlock = e.target.closest('.appointment-block');
            if (appointmentBlock) {
                e.preventDefault();
                this.showContextMenu(e, appointmentBlock);
            } else {
                this.hideContextMenu();
            }
        });

        // Click on context menu items
        this.contextMenu.addEventListener('click', (e) => {
            const item = e.target.closest('.context-menu-item');
            if (item) {
                const action = item.dataset.action;
                this.handleAction(action);
                this.hideContextMenu();
            }
        });

        // Hide context menu on outside click
        document.addEventListener('click', (e) => {
            if (!this.contextMenu.contains(e.target)) {
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

    showContextMenu(event, appointmentBlock) {
        // Extract appointment ID from various possible attributes
        this.currentAppointmentId = this.extractAppointmentId(appointmentBlock);
        
        if (!this.currentAppointmentId) {
            console.warn('No appointment ID found for context menu');
            return;
        }

        // Position the context menu
        const x = event.pageX;
        const y = event.pageY;
        
        this.contextMenu.style.left = x + 'px';
        this.contextMenu.style.top = y + 'px';
        this.contextMenu.style.display = 'block';

        // Adjust position if menu goes off screen
        const rect = this.contextMenu.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;

        if (rect.right > viewportWidth) {
            this.contextMenu.style.left = (x - rect.width) + 'px';
        }
        
        if (rect.bottom > viewportHeight) {
            this.contextMenu.style.top = (y - rect.height) + 'px';
        }
    }

    hideContextMenu() {
        this.contextMenu.style.display = 'none';
        this.currentAppointmentId = null;
    }

    extractAppointmentId(appointmentBlock) {
        // Try different ways to find appointment ID
        return appointmentBlock.dataset.appointmentId ||
               appointmentBlock.dataset.id ||
               appointmentBlock.getAttribute('data-appointment-id') ||
               appointmentBlock.getAttribute('data-id') ||
               appointmentBlock.id?.replace('appointment-', '') ||
               this.extractIdFromOnClick(appointmentBlock);
    }

    extractIdFromOnClick(appointmentBlock) {
        // Try to extract ID from onclick attribute
        const onclick = appointmentBlock.getAttribute('onclick');
        if (onclick) {
            const match = onclick.match(/\d+/);
            return match ? match[0] : null;
        }
        return null;
    }

    handleAction(action) {
        if (!this.currentAppointmentId) {
            alert('No appointment selected');
            return;
        }

        switch (action) {
            case 'go-to-billing':
                this.goToIntegratedBilling();
                break;
            case 'view-details':
                this.viewAppointmentDetails();
                break;
            case 'edit-appointment':
                this.editAppointment();
                break;
            default:
                console.warn('Unknown action:', action);
        }
    }

    goToIntegratedBilling() {
        // Show loading indicator
        this.showLoadingMessage('Redirecting to billing...');
        
        // Redirect to the integrated billing with appointment data
        window.location.href = `/appointment/${this.currentAppointmentId}/go-to-billing`;
    }

    viewAppointmentDetails() {
        if (typeof showAppointmentDetails === 'function') {
            showAppointmentDetails(this.currentAppointmentId);
        } else {
            alert('View details functionality not available');
        }
    }

    editAppointment() {
        if (typeof editAppointment === 'function') {
            editAppointment(this.currentAppointmentId);
        } else {
            alert('Edit functionality not available');
        }
    }

    showLoadingMessage(message) {
        // Create a simple loading overlay
        const overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            color: white;
            font-size: 18px;
        `;
        overlay.innerHTML = `
            <div style="text-align: center;">
                <i class="fas fa-spinner fa-spin fa-2x mb-3"></i>
                <div>${message}</div>
            </div>
        `;
        document.body.appendChild(overlay);
        
        // Remove after 3 seconds as fallback
        setTimeout(() => {
            if (document.getElementById('loading-overlay')) {
                document.body.removeChild(overlay);
            }
        }, 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize context menu
    new AppointmentContextMenu();
    
    console.log('✅ Appointment context menu initialized');
});

// Also initialize if DOM is already loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        new AppointmentContextMenu();
    });
} else {
    new AppointmentContextMenu();
}