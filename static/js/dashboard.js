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
    console.error('Navigation failed:', error);
    if (typeof showNotification === 'function') {
        showNotification('Navigation error occurred. Please try again.', 'error');
    } else {
        alert('Navigation error occurred. Please try again.');
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

// Global variables for dashboard functionality
let inventoryState = {
    consumption: {
        currentPage: 1,
        perPage: 10,
        totalPages: 1,
        data: [],
        allData: [], // For export all functionality
        filters: {
            fromDate: '',
            toDate: '',
            search: ''
        },
        sort: {
            field: 'consumption_date',
            direction: 'desc'
        }
    },
    adjustments: {
        currentPage: 1,
        perPage: 10,
        totalPages: 1,
        data: [],
        allData: [], // For export all functionality
        filters: {
            fromDate: '',
            toDate: '',
            search: ''
        },
        sort: {
            field: 'created_at',
            direction: 'desc'
        }
    }
};

// Initialize default date range (current month)
function initializeDateRanges() {
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const todayStr = today.toISOString().split('T')[0];
    const firstDayStr = firstDay.toISOString().split('T')[0];

    // Set consumption filters
    inventoryState.consumption.filters.fromDate = firstDayStr;
    inventoryState.consumption.filters.toDate = todayStr;

    // Set adjustments filters  
    inventoryState.adjustments.filters.fromDate = firstDayStr;
    inventoryState.adjustments.filters.toDate = todayStr;

    // Update form fields
    document.getElementById('consumption-from-date').value = firstDayStr;
    document.getElementById('consumption-to-date').value = todayStr;
    document.getElementById('adjustments-from-date').value = firstDayStr;
    document.getElementById('adjustments-to-date').value = todayStr;
}

// Load consumption data
async function loadConsumptionData(page = 1) {
    try {
        const params = new URLSearchParams({
            page: page,
            per_page: inventoryState.consumption.perPage,
            from_date: inventoryState.consumption.filters.fromDate,
            to_date: inventoryState.consumption.filters.toDate,
            search: inventoryState.consumption.filters.search,
            sort_by: inventoryState.consumption.sort.field,
            sort_order: inventoryState.consumption.sort.direction
        });

        const response = await fetch(`/api/inventory/consumption?${params}`);
        const data = await response.json();

        if (data.success) {
            inventoryState.consumption.data = data.data;
            inventoryState.consumption.currentPage = data.pagination.page;
            inventoryState.consumption.totalPages = data.pagination.pages;
            renderConsumptionTable();
            renderConsumptionPagination();
        } else {
            console.error('Error loading consumption data:', data.error);
            showAlert('Error loading consumption data', 'error');
        }
    } catch (error) {
        console.error('Error loading consumption data:', error);
        showAlert('Error loading consumption data', 'error');
    }
}

// Load adjustments data
async function loadAdjustmentsData(page = 1) {
    try {
        const params = new URLSearchParams({
            page: page,
            per_page: inventoryState.adjustments.perPage,
            from_date: inventoryState.adjustments.filters.fromDate,
            to_date: inventoryState.adjustments.filters.toDate,
            search: inventoryState.adjustments.filters.search,
            sort_by: inventoryState.adjustments.sort.field,
            sort_order: inventoryState.adjustments.sort.direction
        });

        const response = await fetch(`/api/inventory/adjustments?${params}`);
        const data = await response.json();

        if (data.success) {
            inventoryState.adjustments.data = data.data;
            inventoryState.adjustments.currentPage = data.pagination.page;
            inventoryState.adjustments.totalPages = data.pagination.pages;
            renderAdjustmentsTable();
            renderAdjustmentsPagination();
        } else {
            console.error('Error loading adjustments data:', data.error);
            showAlert('Error loading adjustments data', 'error');
        }
    } catch (error) {
        console.error('Error loading adjustments data:', error);
        showAlert('Error loading adjustments data', 'error');
    }
}

// Render consumption table
function renderConsumptionTable() {
    const tbody = document.getElementById('consumptionTableBody');
    if (!tbody) return;

    if (inventoryState.consumption.data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-3"></i><br>
                    No consumption records found.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = inventoryState.consumption.data.map(record => `
        <tr>
            <td>${new Date(record.created_at).toLocaleDateString()}</td>
            <td>${record.batch_name || 'N/A'}</td>
            <td>${record.product_name || 'N/A'}</td>
            <td>${record.quantity}</td>
            <td>${record.reference || '-'}</td>
            <td>${record.issued_to || '-'}</td>
            <td>-</td>
            <td>
                ${record.notes ? `<span class="text-truncate" style="max-width: 100px;" title="${record.notes}">${record.notes}</span>` : '-'}
            </td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary btn-sm" onclick="editConsumption(${record.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteConsumption(${record.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Render adjustments table
function renderAdjustmentsTable() {
    const tbody = document.getElementById('adjustments-table-body');
    if (!tbody) return;

    if (inventoryState.adjustments.data.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-3"></i><br>
                    No records match your filters.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = inventoryState.adjustments.data.map(record => `
        <tr>
            <td>${record.reference_id}</td>
            <td>${record.adjustment_date}</td>
            <td>${record.quantity}</td>
            <td>$${record.subtotal_value.toFixed(2)}</td>
            <td>$${record.total_value.toFixed(2)}</td>
            <td>
                ${record.remarks ? `<span class="text-truncate" style="max-width: 100px;" title="${record.remarks}">${record.remarks}</span>` : '-'}
            </td>
            <td>${record.created_by}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary btn-sm" onclick="editAdjustment(${record.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteAdjustment(${record.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

// Render pagination
function renderConsumptionPagination() {
    const container = document.getElementById('consumption-pagination');
    if (!container) return;

    renderPagination(container, inventoryState.consumption.currentPage, 
                    inventoryState.consumption.totalPages, 
                    (page) => loadConsumptionData(page));
}

function renderAdjustmentsPagination() {
    const container = document.getElementById('adjustments-pagination');
    if (!container) return;

    renderPagination(container, inventoryState.adjustments.currentPage, 
                    inventoryState.adjustments.totalPages, 
                    (page) => loadAdjustmentsData(page));
}

// Generic pagination renderer
function renderPagination(container, currentPage, totalPages, onPageClick) {
    let html = '';

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    // Previous button
    html += `
        <button class="btn btn-outline-secondary btn-sm me-1 ${currentPage === 1 ? 'disabled' : ''}" 
                onclick="${currentPage > 1 ? `(${onPageClick})(${currentPage - 1})` : 'void(0)'}">
            <i class="fas fa-chevron-left"></i>
        </button>
    `;

    // Page numbers
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        html += `
            <button class="btn ${i === currentPage ? 'btn-primary' : 'btn-outline-secondary'} btn-sm me-1"
                    onclick="(${onPageClick})(${i})">
                ${i}
            </button>
        `;
    }

    // Next button
    html += `
        <button class="btn btn-outline-secondary btn-sm ${currentPage === totalPages ? 'disabled' : ''}" 
                onclick="${currentPage < totalPages ? `(${onPageClick})(${currentPage + 1})` : 'void(0)'}">
            <i class="fas fa-chevron-right"></i>
        </button>
    `;

    container.innerHTML = html;
}

// Filter functions
function applyConsumptionFilters() {
    inventoryState.consumption.filters.fromDate = document.getElementById('consumption-from-date').value;
    inventoryState.consumption.filters.toDate = document.getElementById('consumption-to-date').value;
    inventoryState.consumption.filters.search = document.getElementById('consumption-search').value;
    inventoryState.consumption.currentPage = 1;
    loadConsumptionData();
}

function applyAdjustmentsFilters() {
    inventoryState.adjustments.filters.fromDate = document.getElementById('adjustments-from-date').value;
    inventoryState.adjustments.filters.toDate = document.getElementById('adjustments-to-date').value;
    inventoryState.adjustments.filters.search = document.getElementById('adjustments-search').value;
    inventoryState.adjustments.currentPage = 1;
    loadAdjustmentsData();
}

function resetConsumptionFilters() {
    document.getElementById('consumption-from-date').value = '';
    document.getElementById('consumption-to-date').value = '';
    document.getElementById('consumption-search').value = '';
    inventoryState.consumption.filters = { fromDate: '', toDate: '', search: '' };
    inventoryState.consumption.currentPage = 1;
    loadConsumptionData();
}

function resetAdjustmentsFilters() {
    document.getElementById('adjustments-from-date').value = '';
    document.getElementById('adjustments-to-date').value = '';
    document.getElementById('adjustments-search').value = '';
    inventoryState.adjustments.filters = { fromDate: '', toDate: '', search: '' };
    inventoryState.adjustments.currentPage = 1;
    loadAdjustmentsData();
}

// Sorting functions
function sortConsumption(field) {
    if (inventoryState.consumption.sort.field === field) {
        inventoryState.consumption.sort.direction = 
            inventoryState.consumption.sort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        inventoryState.consumption.sort.field = field;
        inventoryState.consumption.sort.direction = 'desc';
    }
    loadConsumptionData();
    updateSortIcons('consumption', field);
}

function sortAdjustments(field) {
    if (inventoryState.adjustments.sort.field === field) {
        inventoryState.adjustments.sort.direction = 
            inventoryState.adjustments.sort.direction === 'asc' ? 'desc' : 'asc';
    } else {
        inventoryState.adjustments.sort.field = field;
        inventoryState.adjustments.sort.direction = 'desc';
    }
    loadAdjustmentsData();
    updateSortIcons('adjustments', field);
}

function updateSortIcons(tableType, activeField) {
    const headers = document.querySelectorAll(`#${tableType}-table th[data-sort]`);
    headers.forEach(header => {
        const icon = header.querySelector('i');
        const field = header.dataset.sort;

        if (field === activeField) {
            const direction = inventoryState[tableType].sort.direction;
            icon.className = direction === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
        } else {
            icon.className = 'fas fa-sort text-muted';
        }
    });
}

// Page size change handlers
function changeConsumptionPageSize() {
    inventoryState.consumption.perPage = parseInt(document.getElementById('consumption-page-size').value);
    inventoryState.consumption.currentPage = 1;
    loadConsumptionData();
}

function changeAdjustmentsPageSize() {
    inventoryState.adjustments.perPage = parseInt(document.getElementById('adjustments-page-size').value);
    inventoryState.adjustments.currentPage = 1;
    loadAdjustmentsData();
}

// Export functions using SheetJS
async function exportToExcel(type, exportAll = false) {
    try {
        let data = [];
        let filename = '';

        if (type === 'consumption') {
            if (exportAll) {
                // Load all consumption data
                const params = new URLSearchParams({
                    per_page: 10000, // Large number to get all records
                    from_date: '',
                    to_date: '',
                    search: ''
                });
                const response = await fetch(`/api/inventory/consumption?${params}`);
                const result = await response.json();
                data = result.success ? result.data : [];
                filename = 'consumption-all-records.xlsx';
            } else {
                data = inventoryState.consumption.data;
                filename = 'consumption-filtered-records.xlsx';
            }

            // Transform data for Excel
            const excelData = data.map(record => ({
                'Date': record.consumption_date,
                'Product': record.product_name,
                'SKU': record.product_sku,
                'Qty Used': record.quantity_used,
                'Unit': record.unit_of_measure,
                'Issued To': record.issued_to,
                'Reference ID': record.reference_doc_no,
                'Notes': record.notes || ''
            }));

            exportToExcelFile(excelData, filename);

        } else if (type === 'adjustments') {
            if (exportAll) {
                // Load all adjustments data
                const params = new URLSearchParams({
                    per_page: 10000, // Large number to get all records
                    from_date: '',
                    to_date: '',
                    search: ''
                });
                const response = await fetch(`/api/inventory/adjustments?${params}`);
                const result = await response.json();
                data = result.success ? result.data : [];
                filename = 'adjustments-all-records.xlsx';
            } else {
                data = inventoryState.adjustments.data;
                filename = 'adjustments-filtered-records.xlsx';
            }

            // Transform data for Excel
            const excelData = data.map(record => ({
                'Reference ID': record.reference_id,
                'Adjustment Date': record.adjustment_date,
                'Product': record.product_name || '',
                'Quantity': record.quantity,
                'Subtotal Value': record.subtotal_value,
                'Total Value': record.total_value,
                'Remarks': record.remarks,
                'Created By': record.created_by
            }));

            exportToExcelFile(excelData, filename);
        }

    } catch (error) {
        console.error('Export error:', error);
        showAlert('Error exporting data to Excel', 'error');
    }
}

function exportToExcelFile(data, filename) {
    // Create a new workbook and worksheet
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Data");

    // Write the file
    XLSX.writeFile(wb, filename);
    showAlert('Data exported successfully!', 'success');
}

// Placeholder functions for CRUD operations
function editConsumption(id) {
    showAlert('Edit consumption functionality coming soon!', 'info');
}

function deleteConsumption(id) {
    if (confirm('Are you sure you want to delete this consumption record?')) {
        showAlert('Delete consumption functionality coming soon!', 'info');
    }
}

function editAdjustment(id) {
    showAlert('Edit adjustment functionality coming soon!', 'info');
}

function deleteAdjustment(id) {
    if (confirm('Are you sure you want to delete this adjustment record?')) {
        showAlert('Delete adjustment functionality coming soon!', 'info');
    }
}

// Alert function
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertDiv);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}