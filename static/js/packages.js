/**
 * Customer Packages JavaScript - Interactive functionality for package management
 */

// Global variables
let currentPackages = [];
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};
let templates = [];
let customers = [];
let services = [];
let staff = [];
let currentPackageId = null;
let currentPackageDetails = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Customer Packages JS loaded');
    initializePackages();
});

/**
 * Global functions - Define these immediately for inline onclick handlers
 */

// Open assign package modal
function openAssignModal() {
    console.log('Opening assign modal...');
    
    // Reset form
    const form = document.getElementById('assignPackageForm');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    
    const preview = document.getElementById('packagePreview');
    if (preview) {
        preview.style.display = 'none';
    }
    
    // Load data and show modal
    Promise.all([loadTemplates(), loadCustomers()]).then(() => {
        const modal = new bootstrap.Modal(document.getElementById('assignPackageModal'));
        modal.show();
    }).catch(error => {
        console.error('Error loading modal data:', error);
        showToast('Error loading data for assignment', 'error');
    });
}

// Clear all filters
function clearFilters() {
    console.log('Clearing filters...');
    
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    
    if (searchInput) searchInput.value = '';
    if (statusFilter) statusFilter.value = '';
    if (dateFrom) dateFrom.value = '';
    if (dateTo) dateTo.value = '';
    
    // Reset current filters and reload
    currentFilters = {};
    currentPage = 1;
    
    loadPackages();
}

// Apply current filters
function applyFilters() {
    console.log('Applying filters...');
    
    const searchInput = document.getElementById('searchInput');
    const statusFilter = document.getElementById('statusFilter');
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    
    currentFilters = {};
    
    if (searchInput && searchInput.value.trim()) {
        currentFilters.q = searchInput.value.trim();
    }
    
    if (statusFilter && statusFilter.value) {
        currentFilters.status = statusFilter.value;
    }
    
    if (dateFrom && dateFrom.value) {
        currentFilters.date_from = dateFrom.value;
    }
    
    if (dateTo && dateTo.value) {
        currentFilters.date_to = dateTo.value;
    }
    
    currentPage = 1;
    loadPackages();
}

// Open package details modal
function openDetails(packageId) {
    console.log('Opening package details for:', packageId);
    openPackageDetailsModal(packageId);
}

// Open usage recording modal
function openUseModal(packageId) {
    console.log('Opening usage modal for package:', packageId);
    
    if (packageId) {
        currentPackageId = packageId;
        // Load package details first, then open usage modal
        openPackageDetailsModal(packageId).then(() => {
            setTimeout(() => showUsageModal(), 200);
        });
    } else if (currentPackageDetails) {
        showUsageModal();
    } else {
        showToast('Please select a package first', 'warning');
    }
}

// Open adjustment/refund modal
function openAdjustModal(packageId) {
    console.log('Opening adjust modal for package:', packageId);
    
    if (packageId) {
        currentPackageId = packageId;
        // Load package details first, then open adjust modal
        openPackageDetailsModal(packageId).then(() => {
            setTimeout(() => showAdjustModal(), 200);
        });
    } else if (currentPackageDetails) {
        showAdjustModal();
    } else {
        showToast('Please select a package first', 'warning');
    }
}

// Change pagination page
function changePage(page) {
    currentPage = page;
    loadPackages();
}

// Attach functions to window object for global access
window.openAssignModal = openAssignModal;
window.clearFilters = clearFilters;
window.applyFilters = applyFilters;
window.openDetails = openDetails;
window.openUseModal = openUseModal;
window.openAdjustModal = openAdjustModal;
window.changePage = changePage;

/**
 * Initialize the packages system
 */
async function initializePackages() {
    try {
        // Set default date/time
        const now = new Date();
        const dateTimeInput = document.getElementById('usageDateTime');
        if (dateTimeInput) {
            dateTimeInput.value = now.toISOString().slice(0, 16);
        }
        
        // Load initial data
        await Promise.all([
            loadPackages(),
            loadTemplates(),
            loadCustomers(),
            loadServices(),
            loadStaff()
        ]);
        
        // Setup event listeners
        setupEventListeners();
        
        console.log('Customer Packages initialized successfully');
    } catch (error) {
        console.error('Error initializing packages:', error);
        showToast('Error loading packages system', 'error');
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            currentFilters.q = searchInput.value;
            loadPackages();
        }, 500));
    }
    
    // Assign package form validation
    const assignForm = document.getElementById('assignPackageForm');
    if (assignForm) {
        assignForm.addEventListener('input', validateAssignForm);
    }
    
    // Package template selection
    const assignPackage = document.getElementById('assignPackage');
    if (assignPackage) {
        assignPackage.addEventListener('change', showPackagePreview);
    }
    
    // Usage form validation
    const usageForm = document.getElementById('recordUsageForm');
    if (usageForm) {
        usageForm.addEventListener('input', validateUsageForm);
    }
    
    // Usage service/quantity change for hints
    const usageService = document.getElementById('usageService');
    const usageQuantity = document.getElementById('usageQuantity');
    if (usageService && usageQuantity) {
        usageService.addEventListener('change', updateUsageHint);
        usageQuantity.addEventListener('input', updateUsageHint);
    }
    
    // Adjust form validation
    const adjustForm = document.getElementById('adjustRefundForm');
    if (adjustForm) {
        adjustForm.addEventListener('input', validateAdjustForm);
    }
    
    // Adjust service/quantity change for hints
    const adjustService = document.getElementById('adjustService');
    const adjustQuantity = document.getElementById('adjustQuantity');
    if (adjustService && adjustQuantity) {
        adjustService.addEventListener('change', updateAdjustHint);
        adjustQuantity.addEventListener('input', updateAdjustHint);
    }
    
    // Mode toggle for adjust/refund
    const adjustModeInputs = document.querySelectorAll('input[name="adjustMode"]');
    adjustModeInputs.forEach(input => {
        input.addEventListener('change', updateAdjustHint);
    });
    
    // Save buttons
    const saveAssignBtn = document.getElementById('saveAssignPackage');
    if (saveAssignBtn) {
        saveAssignBtn.addEventListener('click', saveAssignment);
    }
    
    const saveUsageBtn = document.getElementById('saveUsage');
    if (saveUsageBtn) {
        saveUsageBtn.addEventListener('click', saveUsage);
    }
    
    const saveAdjustBtn = document.getElementById('saveAdjustment');
    if (saveAdjustBtn) {
        saveAdjustBtn.addEventListener('click', saveAdjustment);
    }
}

/**
 * Load packages with current filters
 */
async function loadPackages() {
    try {
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 20,
            ...currentFilters
        });
        
        const response = await fetch(`/packages/api/customer-packages?${params}`);
        const data = await response.json();
        
        if (data.success) {
            currentPackages = data.packages;
            
            if (data.pagination) {
                currentPage = data.pagination.page;
                totalPages = data.pagination.pages;
                updatePagination(data.pagination);
            }
            
            renderPackagesTable();
        } else {
            showToast(data.error || 'Error loading packages', 'error');
        }
    } catch (error) {
        console.error('Error loading packages:', error);
        showToast('Error loading packages', 'error');
    }
}

/**
 * Load package templates
 */
async function loadTemplates() {
    try {
        const response = await fetch('/packages/api/templates');
        const data = await response.json();
        
        if (data.success) {
            templates = data.templates;
            populateTemplateSelect();
        }
    } catch (error) {
        console.error('Error loading templates:', error);
    }
}

/**
 * Load customers
 */
async function loadCustomers() {
    try {
        const response = await fetch('/packages/api/customers');
        const data = await response.json();
        
        if (data.success) {
            customers = data.customers;
            populateCustomerSelect();
        }
    } catch (error) {
        console.error('Error loading customers:', error);
    }
}

/**
 * Load services
 */
async function loadServices() {
    try {
        const response = await fetch('/packages/api/services');
        const data = await response.json();
        
        if (data.success) {
            services = data.services;
            populateServiceSelects();
        }
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

/**
 * Load staff
 */
async function loadStaff() {
    try {
        const response = await fetch('/packages/api/staff');
        const data = await response.json();
        
        if (data.success) {
            staff = data.staff;
            populateStaffSelect();
        }
    } catch (error) {
        console.error('Error loading staff:', error);
    }
}

/**
 * Populate dropdowns
 */
function populateTemplateSelect() {
    const select = document.getElementById('assignPackage');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select package...</option>';
    templates.forEach(template => {
        const option = document.createElement('option');
        option.value = template.id;
        option.textContent = `${template.name} - $${template.price}`;
        option.dataset.template = JSON.stringify(template);
        select.appendChild(option);
    });
}

function populateCustomerSelect() {
    const select = document.getElementById('assignCustomer');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select customer...</option>';
    customers.forEach(customer => {
        const option = document.createElement('option');
        option.value = customer.id;
        option.textContent = `${customer.name} - ${customer.phone}`;
        select.appendChild(option);
    });
}

function populateServiceSelects() {
    // For usage modal
    const usageSelect = document.getElementById('usageService');
    if (usageSelect) {
        usageSelect.innerHTML = '<option value="">Select service...</option>';
    }
    
    // For adjust modal
    const adjustSelect = document.getElementById('adjustService');
    if (adjustSelect) {
        adjustSelect.innerHTML = '<option value="">Select service...</option>';
    }
}

function populateStaffSelect() {
    const select = document.getElementById('usageStaff');
    if (!select) return;
    
    select.innerHTML = '<option value="">Select staff member...</option>';
    staff.forEach(member => {
        const option = document.createElement('option');
        option.value = member.id;
        option.textContent = `${member.name} (${member.role})`;
        select.appendChild(option);
    });
}

/**
 * Render packages table
 */
function renderPackagesTable() {
    const tbody = document.getElementById('packagesTableBody');
    if (!tbody) return;
    
    if (currentPackages.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-2x mb-2 d-block"></i>
                    No packages found matching your criteria
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = currentPackages.map(pkg => {
        const statusClass = getStatusClass(pkg.status);
        const expiresText = pkg.expires_on ? pkg.expires_on : 'No expiry';
        
        return `
            <tr>
                <td>
                    <strong>${pkg.customer_name}</strong>
                </td>
                <td>${pkg.package_name}</td>
                <td>
                    <small class="text-muted">Assigned:</small> ${pkg.assigned_on}<br>
                    <small class="text-muted">Expires:</small> ${expiresText}
                </td>
                <td><span class="badge bg-primary">${pkg.total_services}</span></td>
                <td><span class="badge bg-warning text-dark">${pkg.used_services}</span></td>
                <td><span class="badge bg-success">${pkg.remaining_services}</span></td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" role="progressbar" 
                             style="width: ${pkg.usage_percentage}%"
                             aria-valuenow="${pkg.usage_percentage}" 
                             aria-valuemin="0" aria-valuemax="100">
                            ${pkg.usage_percentage}%
                        </div>
                    </div>
                </td>
                <td><span class="badge ${statusClass}">${pkg.status}</span></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-primary btn-sm" 
                                onclick="openDetails(${pkg.id})" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${pkg.status === 'active' ? `
                            <button type="button" class="btn btn-outline-success btn-sm" 
                                    onclick="openUseModal(${pkg.id})" title="Record Usage">
                                <i class="fas fa-play"></i>
                            </button>
                            <button type="button" class="btn btn-outline-warning btn-sm" 
                                    onclick="openAdjustModal(${pkg.id})" title="Adjust/Refund">
                                <i class="fas fa-edit"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Get CSS class for status badge
 */
function getStatusClass(status) {
    const classes = {
        'active': 'bg-success',
        'completed': 'bg-primary',
        'expired': 'bg-danger',
        'paused': 'bg-warning text-dark'
    };
    return classes[status] || 'bg-secondary';
}

/**
 * Update pagination
 */
function updatePagination(pagination) {
    const info = document.getElementById('paginationInfo');
    const controls = document.getElementById('paginationControls');
    
    if (info) {
        const start = ((pagination.page - 1) * pagination.per_page) + 1;
        const end = Math.min(pagination.page * pagination.per_page, pagination.total);
        info.textContent = `Showing ${start}-${end} of ${pagination.total} packages`;
    }
    
    if (controls) {
        let html = '';
        
        // Previous button
        if (pagination.has_prev) {
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${pagination.page - 1})">
                        <i class="fas fa-chevron-left"></i>
                    </a>
                </li>
            `;
        }
        
        // Page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);
        
        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === pagination.page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
                </li>
            `;
        }
        
        // Next button
        if (pagination.has_next) {
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" onclick="changePage(${pagination.page + 1})">
                        <i class="fas fa-chevron-right"></i>
                    </a>
                </li>
            `;
        }
        
        controls.innerHTML = html;
    }
}

/**
 * Change page
 */
function changePage(page) {
    currentPage = page;
    loadPackages();
}

/**
 * Open assign package modal
 */
async function openAssignModal() {
    // Reset form
    document.getElementById('assignPackageForm').reset();
    document.getElementById('packagePreview').style.display = 'none';
    
    // Set default price if package is selected
    const assignPackageSelect = document.getElementById('assignPackage');
    if (assignPackageSelect.value) {
        const selectedOption = assignPackageSelect.selectedOptions[0];
        const template = JSON.parse(selectedOption.dataset.template);
        document.getElementById('assignPrice').value = template.price;
    }
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('assignPackageModal'));
    modal.show();
}

/**
 * Show package preview when template is selected
 */
function showPackagePreview() {
    const select = document.getElementById('assignPackage');
    const preview = document.getElementById('packagePreview');
    const itemsContainer = document.getElementById('packageItems');
    const priceInput = document.getElementById('assignPrice');
    
    if (select.value) {
        const selectedOption = select.selectedOptions[0];
        const template = JSON.parse(selectedOption.dataset.template);
        
        // Set default price
        priceInput.value = template.price;
        
        // Show items
        itemsContainer.innerHTML = template.items.map(item => `
            <div class="col-md-6">
                <div class="card border-secondary">
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="fw-bold">${item.service_name}</span>
                            <span class="badge bg-primary">${item.qty}</span>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
        
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
        priceInput.value = '';
    }
    
    validateAssignForm();
}

/**
 * Validate assign form
 */
function validateAssignForm() {
    const form = document.getElementById('assignPackageForm');
    const saveBtn = document.getElementById('saveAssignPackage');
    
    const customer = document.getElementById('assignCustomer').value;
    const package = document.getElementById('assignPackage').value;
    const price = document.getElementById('assignPrice').value;
    
    const isValid = customer && package && price && parseFloat(price) > 0;
    
    saveBtn.disabled = !isValid;
    
    // Show validation feedback
    form.classList.toggle('was-validated', isValid);
}

/**
 * Save package assignment
 */
async function saveAssignment() {
    try {
        const formData = {
            customer_id: parseInt(document.getElementById('assignCustomer').value),
            package_id: parseInt(document.getElementById('assignPackage').value),
            price_paid: parseFloat(document.getElementById('assignPrice').value),
            discount: parseFloat(document.getElementById('assignDiscount').value) || 0,
            notes: document.getElementById('assignNotes').value
        };
        
        const expiresInput = document.getElementById('assignExpires');
        if (expiresInput.value) {
            formData.expires_on = expiresInput.value + 'T23:59:59';
        }
        
        const response = await fetch('/packages/api/assign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Package assigned successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignPackageModal'));
            modal.hide();
            
            // Reload packages
            await loadPackages();
        } else {
            showToast(data.error || 'Error assigning package', 'error');
        }
    } catch (error) {
        console.error('Error saving assignment:', error);
        showToast('Error assigning package', 'error');
    }
}

/**
 * Open package details modal (renamed to avoid conflict)
 */
async function openPackageDetailsModal(packageId) {
    try {
        currentPackageId = packageId;
        
        const response = await fetch(`/packages/api/customer-packages/${packageId}`);
        const data = await response.json();
        
        if (data.success) {
            currentPackageDetails = data.package;
            renderPackageDetails();
            
            const modal = new bootstrap.Modal(document.getElementById('packageDetailsModal'));
            modal.show();
            
            return Promise.resolve();
        } else {
            showToast(data.error || 'Error loading package details', 'error');
            return Promise.reject(data.error);
        }
    } catch (error) {
        console.error('Error loading package details:', error);
        showToast('Error loading package details', 'error');
        return Promise.reject(error);
    }
}

/**
 * Show usage modal with current package data
 */
function showUsageModal() {
    if (!currentPackageDetails) {
        showToast('Package details not loaded', 'error');
        return;
    }
    
    // Reset form
    const form = document.getElementById('recordUsageForm');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    
    // Set current date/time
    const now = new Date();
    const dateTimeInput = document.getElementById('usageDateTime');
    if (dateTimeInput) {
        dateTimeInput.value = now.toISOString().slice(0, 16);
    }
    
    // Populate services from package items
    const serviceSelect = document.getElementById('usageService');
    if (serviceSelect) {
        serviceSelect.innerHTML = '<option value="">Select service...</option>';
        
        if (currentPackageDetails.items) {
            currentPackageDetails.items.forEach(item => {
                if (item.remaining_qty > 0) {
                    const option = document.createElement('option');
                    option.value = item.service_id;
                    option.textContent = `${item.service_name} (${item.remaining_qty} remaining)`;
                    option.dataset.remaining = item.remaining_qty;
                    serviceSelect.appendChild(option);
                }
            });
        }
    }
    
    // Hide hints
    const hint = document.getElementById('usageHint');
    if (hint) {
        hint.style.display = 'none';
    }
    
    const modal = new bootstrap.Modal(document.getElementById('recordUsageModal'));
    modal.show();
}

/**
 * Show adjustment modal with current package data
 */
function showAdjustModal() {
    if (!currentPackageDetails) {
        showToast('Package details not loaded', 'error');
        return;
    }
    
    // Reset form
    const form = document.getElementById('adjustRefundForm');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    
    // Set default mode to refund
    const refundMode = document.getElementById('refundMode');
    if (refundMode) {
        refundMode.checked = true;
    }
    
    // Populate services from package items
    const serviceSelect = document.getElementById('adjustService');
    if (serviceSelect) {
        serviceSelect.innerHTML = '<option value="">Select service...</option>';
        
        if (currentPackageDetails.items) {
            currentPackageDetails.items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.service_id;
                option.textContent = `${item.service_name} (${item.used_qty} used, ${item.remaining_qty} remaining)`;
                option.dataset.used = item.used_qty;
                option.dataset.remaining = item.remaining_qty;
                option.dataset.total = item.total_qty;
                serviceSelect.appendChild(option);
            });
        }
    }
    
    // Hide hints
    const hint = document.getElementById('adjustHint');
    if (hint) {
        hint.style.display = 'none';
    }
    
    const modal = new bootstrap.Modal(document.getElementById('adjustRefundModal'));
    modal.show();
}

/**
 * Render package details in modal
 */
function renderPackageDetails() {
    if (!currentPackageDetails) return;
    
    const pkg = currentPackageDetails;
    
    // Header info
    document.getElementById('detailCustomerName').textContent = pkg.customer_name;
    document.getElementById('detailPackageName').textContent = pkg.package_name;
    document.getElementById('detailPrice').textContent = pkg.price_paid.toFixed(2);
    document.getElementById('detailAssigned').textContent = pkg.assigned_on;
    document.getElementById('detailExpires').textContent = pkg.expires_on || 'No expiry';
    
    const statusBadge = document.getElementById('detailStatus');
    statusBadge.textContent = pkg.status;
    statusBadge.className = `badge ${getStatusClass(pkg.status)}`;
    
    // Service items
    const serviceItems = document.getElementById('serviceItems');
    serviceItems.innerHTML = pkg.items.map(item => {
        const progressPercent = item.total_qty > 0 ? ((item.used_qty / item.total_qty) * 100).toFixed(1) : 0;
        
        return `
            <div class="col-md-6 mb-2">
                <div class="card border-secondary">
                    <div class="card-body p-3">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="card-title mb-0">${item.service_name}</h6>
                            <span class="badge bg-primary">${item.used_qty}/${item.total_qty}</span>
                        </div>
                        <div class="progress mb-1" style="height: 8px;">
                            <div class="progress-bar" style="width: ${progressPercent}%"></div>
                        </div>
                        <small class="text-muted">Remaining: ${item.remaining_qty}</small>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    // Recent usage
    const usageTable = document.getElementById('recentUsageTable');
    if (pkg.recent_usage.length === 0) {
        usageTable.innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-muted">No usage recorded yet</td>
            </tr>
        `;
    } else {
        usageTable.innerHTML = pkg.recent_usage.map(usage => `
            <tr>
                <td>${usage.usage_date}</td>
                <td>${usage.service_name}</td>
                <td>${usage.qty}</td>
                <td>
                    <span class="badge ${usage.change_type === 'use' ? 'bg-success' : 
                          usage.change_type === 'refund' ? 'bg-warning' : 'bg-info'}">
                        ${usage.change_type}
                    </span>
                </td>
                <td>${usage.staff_name}</td>
                <td>${usage.notes}</td>
            </tr>
        `).join('');
    }
}

/**
 * Open record usage modal
 */
function openUseModal(packageId = null) {
    if (packageId) {
        currentPackageId = packageId;
        openDetails(packageId).then(() => {
            setTimeout(() => openUseModal(), 100);
        });
        return;
    }
    
    if (!currentPackageDetails) return;
    
    // Reset form
    document.getElementById('recordUsageForm').reset();
    
    // Set current date/time
    const now = new Date();
    document.getElementById('usageDateTime').value = now.toISOString().slice(0, 16);
    
    // Populate services from package items
    const serviceSelect = document.getElementById('usageService');
    serviceSelect.innerHTML = '<option value="">Select service...</option>';
    
    currentPackageDetails.items.forEach(item => {
        if (item.remaining_qty > 0) {
            const option = document.createElement('option');
            option.value = item.service_id;
            option.textContent = `${item.service_name} (${item.remaining_qty} remaining)`;
            option.dataset.remaining = item.remaining_qty;
            serviceSelect.appendChild(option);
        }
    });
    
    // Hide hints
    document.getElementById('usageHint').style.display = 'none';
    
    const modal = new bootstrap.Modal(document.getElementById('recordUsageModal'));
    modal.show();
}

/**
 * Update usage hint
 */
function updateUsageHint() {
    const serviceSelect = document.getElementById('usageService');
    const quantityInput = document.getElementById('usageQuantity');
    const hint = document.getElementById('usageHint');
    const hintText = document.getElementById('usageHintText');
    
    if (serviceSelect.value && quantityInput.value) {
        const selectedOption = serviceSelect.selectedOptions[0];
        const remaining = parseInt(selectedOption.dataset.remaining);
        const quantity = parseInt(quantityInput.value);
        
        if (quantity > remaining) {
            hintText.textContent = `Not enough balance! Only ${remaining} remaining.`;
            hint.className = 'alert alert-danger';
        } else {
            const newRemaining = remaining - quantity;
            hintText.textContent = `Remaining after this usage: ${newRemaining}`;
            hint.className = 'alert alert-info';
        }
        
        hint.style.display = 'block';
    } else {
        hint.style.display = 'none';
    }
    
    validateUsageForm();
}

/**
 * Validate usage form
 */
function validateUsageForm() {
    const form = document.getElementById('recordUsageForm');
    const saveBtn = document.getElementById('saveUsage');
    
    const service = document.getElementById('usageService').value;
    const quantity = document.getElementById('usageQuantity').value;
    
    let isValid = service && quantity && parseInt(quantity) > 0;
    
    // Check if enough balance
    if (isValid && service) {
        const selectedOption = document.getElementById('usageService').selectedOptions[0];
        const remaining = parseInt(selectedOption.dataset.remaining);
        isValid = parseInt(quantity) <= remaining;
    }
    
    saveBtn.disabled = !isValid;
    form.classList.toggle('was-validated', isValid);
}

/**
 * Save usage
 */
async function saveUsage() {
    try {
        const formData = {
            service_id: parseInt(document.getElementById('usageService').value),
            qty: parseInt(document.getElementById('usageQuantity').value),
            notes: document.getElementById('usageNotes').value
        };
        
        const dateTimeInput = document.getElementById('usageDateTime');
        if (dateTimeInput.value) {
            formData.usage_date = dateTimeInput.value + ':00';
        }
        
        const staffInput = document.getElementById('usageStaff');
        if (staffInput.value) {
            formData.staff_id = parseInt(staffInput.value);
        }
        
        const response = await fetch(`/packages/api/customer-packages/${currentPackageId}/use`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('Usage recorded successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('recordUsageModal'));
            modal.hide();
            
            // Reload details and packages
            await Promise.all([
                openDetails(currentPackageId),
                loadPackages()
            ]);
        } else {
            showToast(data.error || 'Error recording usage', 'error');
        }
    } catch (error) {
        console.error('Error saving usage:', error);
        showToast('Error recording usage', 'error');
    }
}

/**
 * Open adjust/refund modal
 */
function openAdjustModal(packageId = null) {
    if (packageId) {
        currentPackageId = packageId;
        openDetails(packageId).then(() => {
            setTimeout(() => openAdjustModal(), 100);
        });
        return;
    }
    
    if (!currentPackageDetails) return;
    
    // Reset form
    document.getElementById('adjustRefundForm').reset();
    document.getElementById('refundMode').checked = true;
    
    // Populate services from package items
    const serviceSelect = document.getElementById('adjustService');
    serviceSelect.innerHTML = '<option value="">Select service...</option>';
    
    currentPackageDetails.items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.service_id;
        option.textContent = `${item.service_name} (${item.used_qty} used, ${item.remaining_qty} remaining)`;
        option.dataset.used = item.used_qty;
        option.dataset.remaining = item.remaining_qty;
        option.dataset.total = item.total_qty;
        serviceSelect.appendChild(option);
    });
    
    // Hide hints
    document.getElementById('adjustHint').style.display = 'none';
    
    const modal = new bootstrap.Modal(document.getElementById('adjustRefundModal'));
    modal.show();
}

/**
 * Update adjust hint
 */
function updateAdjustHint() {
    const serviceSelect = document.getElementById('adjustService');
    const quantityInput = document.getElementById('adjustQuantity');
    const hint = document.getElementById('adjustHint');
    const hintText = document.getElementById('adjustHintText');
    const mode = document.querySelector('input[name="adjustMode"]:checked').value;
    
    if (serviceSelect.value && quantityInput.value) {
        const selectedOption = serviceSelect.selectedOptions[0];
        const used = parseInt(selectedOption.dataset.used);
        const remaining = parseInt(selectedOption.dataset.remaining);
        const total = parseInt(selectedOption.dataset.total);
        const quantity = parseInt(quantityInput.value);
        
        if (mode === 'refund') {
            if (quantity > used) {
                hintText.textContent = `Cannot refund more than used! Only ${used} used.`;
                hint.className = 'alert alert-danger';
            } else {
                const newRemaining = remaining + quantity;
                hintText.textContent = `New remaining after refund: ${newRemaining}`;
                hint.className = 'alert alert-info';
            }
        } else { // adjust
            const newTotal = total + quantity;
            const newRemaining = newTotal - used;
            if (newRemaining < 0) {
                hintText.textContent = `Adjustment would result in negative remaining balance!`;
                hint.className = 'alert alert-danger';
            } else {
                hintText.textContent = `New remaining after adjustment: ${newRemaining}`;
                hint.className = 'alert alert-info';
            }
        }
        
        hint.style.display = 'block';
    } else {
        hint.style.display = 'none';
    }
    
    validateAdjustForm();
}

/**
 * Validate adjust form
 */
function validateAdjustForm() {
    const form = document.getElementById('adjustRefundForm');
    const saveBtn = document.getElementById('saveAdjustment');
    
    const service = document.getElementById('adjustService').value;
    const quantity = document.getElementById('adjustQuantity').value;
    const reason = document.getElementById('adjustReason').value;
    const mode = document.querySelector('input[name="adjustMode"]:checked').value;
    
    let isValid = service && quantity && parseInt(quantity) > 0 && reason.trim();
    
    // Check specific mode validations
    if (isValid && service) {
        const selectedOption = document.getElementById('adjustService').selectedOptions[0];
        const used = parseInt(selectedOption.dataset.used);
        const total = parseInt(selectedOption.dataset.total);
        const qty = parseInt(quantity);
        
        if (mode === 'refund') {
            isValid = qty <= used;
        } else { // adjust
            const newTotal = total + qty;
            const newRemaining = newTotal - used;
            isValid = newRemaining >= 0;
        }
    }
    
    saveBtn.disabled = !isValid;
    form.classList.toggle('was-validated', isValid);
}

/**
 * Save adjustment
 */
async function saveAdjustment() {
    try {
        const mode = document.querySelector('input[name="adjustMode"]:checked').value;
        
        const formData = {
            service_id: parseInt(document.getElementById('adjustService').value),
            qty: parseInt(document.getElementById('adjustQuantity').value),
            reason: document.getElementById('adjustReason').value,
            change_type: mode
        };
        
        const response = await fetch(`/packages/api/customer-packages/${currentPackageId}/adjust`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`${mode === 'refund' ? 'Refund' : 'Adjustment'} processed successfully!`, 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('adjustRefundModal'));
            modal.hide();
            
            // Reload details and packages
            await Promise.all([
                openDetails(currentPackageId),
                loadPackages()
            ]);
        } else {
            showToast(data.error || 'Error processing adjustment', 'error');
        }
    } catch (error) {
        console.error('Error saving adjustment:', error);
        showToast('Error processing adjustment', 'error');
    }
}

/**
 * Apply filters
 */
function applyFilters() {
    currentFilters = {};
    
    const status = document.getElementById('statusFilter').value;
    if (status) currentFilters.status = status;
    
    const dateFrom = document.getElementById('dateFrom').value;
    if (dateFrom) currentFilters.date_from = dateFrom;
    
    const dateTo = document.getElementById('dateTo').value;
    if (dateTo) currentFilters.date_to = dateTo;
    
    currentPage = 1;
    loadPackages();
}

/**
 * Clear filters
 */
function clearFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('statusFilter').value = '';
    document.getElementById('dateFrom').value = '';
    document.getElementById('dateTo').value = '';
    
    currentFilters = {};
    currentPage = 1;
    loadPackages();
}

/**
 * Utility functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showToast(message, type = 'info') {
    // Use the existing notification system if available
    if (typeof showNotification === 'function') {
        showNotification(message, type);
    } else {
        // Fallback to console
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        // You could also create a simple toast here
        alert(message);
    }
}

/**
 * Format numbers and dates
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString();
}

// ========================================
// GLOBAL FUNCTION ATTACHMENTS
// ========================================
// Attach functions to global scope for inline onclick handlers

window.openAssignModal = openAssignModal;
window.openDetails = openDetails;
window.openUseModal = openUseModal;
window.openAdjustModal = openAdjustModal;
window.clearFilters = clearFilters;
window.applyFilters = applyFilters;
window.changePage = changePage;