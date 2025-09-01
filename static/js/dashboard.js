// Dashboard specific JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    
    // Auto-refresh dashboard data every 5 minutes
    setInterval(refreshDashboardData, 300000);
    
    // Setup button click handlers
    setupDashboardButtonHandlers();
});

function setupDashboardButtonHandlers() {
    // Handle quick action buttons
    const quickActionButtons = document.querySelectorAll('.btn-group .btn');
    quickActionButtons.forEach(button => {
        // Add click handler as backup
        button.addEventListener('click', function(e) {
            const action = this.getAttribute('data-action');
            
            if (action && !this.onclick) {
                e.preventDefault();
                console.log('Using backup navigation for:', action);
                
                // Add loading state
                const originalContent = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                this.disabled = true;
                
                // Navigate based on action
                setTimeout(() => {
                    switch(action) {
                        case 'bookings':
                            window.location.href = '/bookings';
                            break;
                        case 'clients':
                            window.location.href = '/clients';
                            break;
                        case 'staff':
                            window.location.href = '/comprehensive_staff';
                            break;
                        case 'checkin':
                            window.location.href = '/checkin';
                            break;
                        default:
                            console.warn('Unknown action:', action);
                            this.innerHTML = originalContent;
                            this.disabled = false;
                    }
                }, 100);
                
                // Reset button after 3 seconds if navigation doesn't complete
                setTimeout(() => {
                    if (this.innerHTML.includes('Loading...')) {
                        this.innerHTML = originalContent;
                        this.disabled = false;
                    }
                }, 3000);
            }
        });
    });
    
    // Handle navigation links in the dashboard
    const dashboardLinks = document.querySelectorAll('a[href]');
    dashboardLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('/')) {
                // Add loading indicator for internal navigation
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
                
                // Reset after delay if navigation doesn't complete
                setTimeout(() => {
                    if (this.innerHTML.includes('Loading...')) {
                        this.innerHTML = originalText;
                    }
                }, 3000);
            }
        });
    });
}

function initializeDashboard() {
    // Initialize charts and widgets
    initializeCharts();
    updateDateTime();
    setupNotifications();
    
    // Update time every minute
    setInterval(updateDateTime, 60000);
}

function initializeCharts() {
    // Revenue trend chart
    const revenueCtx = document.getElementById('revenueTrendChart');
    if (revenueCtx) {
        createRevenueTrendChart(revenueCtx);
    }
    
    // Appointment status chart
    const statusCtx = document.getElementById('appointmentStatusChart');
    if (statusCtx) {
        createAppointmentStatusChart(statusCtx);
    }
    
    // Service popularity chart
    const serviceCtx = document.getElementById('servicePopularityChart');
    if (serviceCtx) {
        createServicePopularityChart(serviceCtx);
    }
}

function createRevenueTrendChart(ctx) {
    // Get last 7 days of revenue data
    const last7Days = getLast7Days();
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: last7Days.map(date => date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
            datasets: [{
                label: 'Daily Revenue',
                data: generateSampleRevenueData(7), // Replace with actual data
                borderColor: '#4e73df',
                backgroundColor: 'rgba(78, 115, 223, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(0);
                        }
                    }
                }
            },
            elements: {
                point: {
                    radius: 4,
                    hoverRadius: 6
                }
            }
        }
    });
}

function createAppointmentStatusChart(ctx) {
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Scheduled', 'Confirmed', 'In Progress', 'Completed', 'Cancelled'],
            datasets: [{
                data: [15, 25, 5, 45, 10], // Replace with actual data
                backgroundColor: [
                    '#36b9cc',
                    '#1cc88a',
                    '#f6c23e',
                    '#5a5c69',
                    '#e74a3b'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                }
            }
        }
    });
}

function createServicePopularityChart(ctx) {
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Haircut', 'Facial', 'Massage', 'Manicure', 'Pedicure'],
            datasets: [{
                label: 'Bookings',
                data: [35, 28, 22, 18, 15], // Replace with actual data
                backgroundColor: '#5a5c69',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    }
                }
            }
        }
    });
}

function updateDateTime() {
    const now = new Date();
    const dateTimeElement = document.getElementById('currentDateTime');
    
    if (dateTimeElement) {
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        
        dateTimeElement.textContent = now.toLocaleDateString('en-US', options);
    }
}

function setupNotifications() {
    // Check for important alerts
    checkLowStockAlerts();
    checkExpiringItems();
    checkUpcomingAppointments();
}

function checkLowStockAlerts() {
    // Simulate checking for low stock items
    const lowStockCount = document.querySelector('[data-low-stock-count]');
    if (lowStockCount && parseInt(lowStockCount.textContent) > 0) {
        showNotification('Low Stock Alert', 'Some inventory items are running low', 'warning');
    }
}

function checkExpiringItems() {
    // Simulate checking for expiring items
    const expiringCount = document.querySelector('[data-expiring-count]');
    if (expiringCount && parseInt(expiringCount.textContent) > 0) {
        showNotification('Expiring Items', 'Some items are expiring soon', 'danger');
    }
}

function checkUpcomingAppointments() {
    // Check for appointments in the next hour
    const now = new Date();
    const nextHour = new Date(now.getTime() + 60 * 60 * 1000);
    
    // This would normally fetch from the server
    // For now, just show a sample notification
    setTimeout(() => {
        showNotification('Upcoming Appointment', 'Next appointment in 30 minutes', 'info');
    }, 2000);
}

function showNotification(title, message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification`;
    notification.innerHTML = `
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.notification-container');
    if (container) {
        container.appendChild(notification);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

function refreshDashboardData() {
    // Refresh dashboard statistics
    console.log('Refreshing dashboard data...');
    
    // In a real implementation, this would fetch updated data from the server
    // and update the dashboard widgets
    
    // Add loading indicator
    const statsCards = document.querySelectorAll('.card[data-stat]');
    statsCards.forEach(card => {
        card.classList.add('loading');
    });
    
    // Simulate API call delay
    setTimeout(() => {
        statsCards.forEach(card => {
            card.classList.remove('loading');
        });
        
        // Update last refresh time
        const lastRefresh = document.getElementById('lastRefresh');
        if (lastRefresh) {
            lastRefresh.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }, 1000);
}

function getLast7Days() {
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date);
    }
    return days;
}

function generateSampleRevenueData(days) {
    // Generate sample revenue data for demonstration
    const data = [];
    for (let i = 0; i < days; i++) {
        data.push(Math.floor(Math.random() * 1000) + 200);
    }
    return data;
}

// Quick action handlers
function quickAddAppointment() {
    try {
        window.location.href = '/bookings';
    } catch (error) {
        console.error('Navigation error:', error);
        handleNavigationError(error);
    }
}

// Prevent multiple dashboard initializations
let dashboardInitialized = false;

function initializeDashboard() {
    if (dashboardInitialized) {
        return;
    }
    dashboardInitialized = true;
    
    console.log('Dashboard loaded successfully');
    console.log('Dashboard JavaScript loaded and ready');
    
    // Initialize dashboard-specific functionality here
    try {
        // Initialize charts if they exist
        if (typeof Chart !== 'undefined' && document.getElementById('revenueChart')) {
            initializeCharts();
        }
        
        // Initialize any dashboard widgets
        initializeDashboardWidgets();
        
    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

function initializeCharts() {
    try {
        // Revenue chart
        const revenueCtx = document.getElementById('revenueChart');
        if (revenueCtx) {
            // Chart initialization code here
        }
        
        // Other charts
        const appointmentCtx = document.getElementById('appointmentChart');
        if (appointmentCtx) {
            // Chart initialization code here
        }
        
    } catch (error) {
        console.error('Chart initialization error:', error);
    }
}

function initializeDashboardWidgets() {
    try {
        // Initialize any dashboard-specific widgets
        console.log('Dashboard widgets initialized');
    } catch (error) {
        console.error('Widget initialization error:', error);
    }
}

function refreshDashboardData() {
    try {
        console.log('Refreshing dashboard data...');
        // Refresh dashboard data without page reload
        // Implementation would go here
    } catch (error) {
        console.error('Dashboard refresh error:', error);
    }
}

// Navigation functions with proper error handling
function quickAddAppointment() {
    try {
        const modal = document.getElementById('addAppointmentModal');
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } else {
            window.location.href = '/bookings';
        }
    } catch (error) {
        console.error('Navigation error:', error);
        handleNavigationError(error);
    }
}

function quickAddClient() {
    try {
        const modal = document.getElementById('addClientModal');
        if (modal) {
            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        } else {
            window.location.href = '/clients';
        }
    } catch (error) {
        console.error('Navigation error:', error);
        window.location.href = '/clients';
    }
}

function quickViewReports() {
    try {
        window.location.href = '/reports';
    } catch (error) {
        console.error('Navigation error:', error);
        handleNavigationError(error);
    }
}

function quickCheckInventory() {
    try {
        window.location.href = '/inventory';
    } catch (error) {
        console.error('Navigation error:', error);
        handleNavigationError(error);
    }
}

function navigateToStaffManagement() {
    try {
        console.log('Navigating to staff management...');
        window.location.href = '/comprehensive_staff';
    } catch (error) {
        console.error('Staff management navigation error:', error);
        handleNavigationError(error);
    }
}

function handleNavigationError(error) {
    console.error('Navigation error:', error);
    if (typeof showAlert === 'function') {
        showAlert('Navigation error occurred. Please try again.', 'warning');
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        initializeDashboard();
    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
});

// Make functions globally available
window.navigateToStaffManagement = navigateToStaffManagement;
window.quickAddAppointment = quickAddAppointment;
window.quickAddClient = quickAddClient;
window.quickViewReports = quickViewReports;
window.quickCheckInventory = quickCheckInventory;
window.refreshDashboardData = refreshDashboardData;
function handleNavigationError(error) {
    console.error('Navigation failed:', error);
    if (typeof showNotification === 'function') {
        showNotification('Navigation error occurred. Please try again.', 'error');
    } else {
        alert('Navigation error occurred. Please try again.');
    }
}

// Export functions
function exportDashboardData() {
    // Simulate exporting dashboard data
    const data = {
        date: new Date().toISOString(),
        stats: {
            appointments: document.querySelector('[data-stat="appointments"]')?.textContent || '0',
            revenue: document.querySelector('[data-stat="revenue"]')?.textContent || '$0',
            clients: document.querySelector('[data-stat="clients"]')?.textContent || '0'
        },
        alerts: {
            lowStock: document.querySelector('[data-low-stock-count]')?.textContent || '0',
            expiring: document.querySelector('[data-expiring-count]')?.textContent || '0'
        }
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Alt + A for new appointment
    if (e.altKey && e.key === 'a') {
        e.preventDefault();
        quickAddAppointment();
    }
    
    // Alt + C for new client
    if (e.altKey && e.key === 'c') {
        e.preventDefault();
        quickAddClient();
    }
    
    // Alt + R for reports
    if (e.altKey && e.key === 'r') {
        e.preventDefault();
        quickViewReports();
    }
});

// Widget resize handler
window.addEventListener('resize', function() {
    // Refresh charts on window resize
    Chart.helpers.each(Chart.instances, function(instance) {
        instance.resize();
    });
});
