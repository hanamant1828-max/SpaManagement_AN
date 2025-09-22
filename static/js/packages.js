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

    // Initialize kitty party modals
    initializeKittyPartyModals();

    // Initialize student offer modals
    initializeStudentOfferModals();

    // Setup event listeners for tables
    setupTableEventDelegation();
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

// ========================================
// GLOBAL FUNCTION ATTACHMENTS - ENSURE PROPER SCOPE
// ========================================

// Define functions that need to be called from HTML onclick handlers
function attachGlobalFunctions() {
    // Make functions available globally for onclick handlers
    window.openAssignModal = openAssignModal;
    window.clearFilters = clearFilters;
    window.applyFilters = applyFilters;
    window.openDetails = openDetails;
    window.openUseModal = openUseModal;
    window.openAdjustModal = openAdjustModal;
    window.changePage = changePage;

    console.log('All global functions attached successfully');
}

// Call immediately after DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    attachGlobalFunctions();
});

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

    // For assigning service packages directly
    const assignServiceSelect = document.getElementById('assign_service_id');
    if (assignServiceSelect) {
        assignServiceSelect.innerHTML = '<option value="">Select service...</option>';
        services.forEach(service => {
            const option = document.createElement('option');
            option.value = service.id;
            option.textContent = `${service.name} - $${service.price}`;
            assignServiceSelect.appendChild(option);
        });
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
function openAssignPackageModal(packageId, packageName, packageType, packagePrice = null) {
    // Set package details
    document.getElementById('assign_package_id').value = packageId;
    document.getElementById('assign_package_name').value = packageName;
    document.getElementById('assign_package_type').value = packageType;

    // Display package info
    document.getElementById('display_package_name').textContent = packageName;
    document.getElementById('display_package_type').textContent = packageType.replace('_', ' ').toUpperCase();

    // Reset form
    document.getElementById('assignPackageForm').reset();
    document.getElementById('assign_package_id').value = packageId;
    document.getElementById('assign_package_name').value = packageName;
    document.getElementById('assign_package_type').value = packageType;

    // Set default price if provided
    if (packagePrice) {
        document.getElementById('assign_custom_price').value = packagePrice;
    }

    // Update modal title
    document.getElementById('assignPackageModalTitle').innerHTML =
        `<i class="fas fa-user-plus me-2"></i>Assign "${packageName}" to Customer`;

    // Focus on customer select
    setTimeout(() => {
        document.getElementById('assign_customer_id').focus();
    }, 300);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('assignPackageModal'));
    modal.show();
}

// Global PackagesUI namespace for assign from template functionality
window.PackagesUI = window.PackagesUI || {};

// Event delegation for prepaid assignment
document.addEventListener('click', e => {
    const b = e.target.closest('[data-action="assign-prepaid"]');
    if (!b) return;
    PackagesUI.assignPrepaidFromTemplate(b.dataset.templateId);
});

// Assign prepaid from template function
function assignPrepaidFromTemplate(templateId) {
    console.log('Assigning prepaid from template:', templateId);

    // Show loading state
    showToast('Loading package template...', 'info');

    // Fetch template details and open modal
    fetch(`/packages/api/templates/${templateId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                openPrepaidAssignModal(data.template);
            } else {
                throw new Error(data.error || 'Failed to load template');
            }
        })
        .catch(error => {
            console.error('Error loading template:', error);
            showToast('Error loading template: ' + error.message, 'error');
        });
}

// Open prepaid assign modal with template data
function openPrepaidAssignModal(template) {
    console.log('Opening prepaid assign modal with template:', template);

    // Populate template data
    document.getElementById('apTemplateName').value = template.name;
    document.getElementById('apTemplateId').value = template.id;
    document.getElementById('apPayAmount').value = template.pay_amount || template.actual_price || 0;
    document.getElementById('apGetValue').value = template.get_value || template.after_value || 0;
    document.getElementById('apBenefit').value = template.benefit_percent || 0;
    document.getElementById('apValidity').value = template.validity_months || 3;
    document.getElementById('apPricePaid').value = template.pay_amount || template.actual_price || 0;

    // Clear other fields
    document.getElementById('apCustomer').value = '';
    document.getElementById('apService').value = '';
    document.getElementById('apExpiresOn').value = '';
    document.getElementById('apNotes').value = '';

    // Load customers and services
    Promise.all([loadCustomersForPrepaid(), loadServicesForPrepaid()])
        .then(() => {
            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('assignPrepaidModal'));
            modal.show();

            // Focus on customer select
            setTimeout(() => {
                document.getElementById('apCustomer').focus();
            }, 300);

            // Update form validation
            validatePrepaidForm();
        })
        .catch(error => {
            console.error('Error loading modal data:', error);
            showToast('Error loading data for assignment', 'error');
        });
}

// Service Package Form Submission
function submitServiceForm() {
    console.log('Submitting service package form...');

    try {
        const form = document.getElementById('servicePackageForm');
        if (!form) {
            console.error('Service package form not found');
            return;
        }

        const formData = new FormData(form);

        // Validate required fields
        const packageName = formData.get('name');
        const payFor = formData.get('pay_for');
        const totalServices = formData.get('total_services');

        if (!packageName || !payFor || !totalServices) {
            alert('Please fill in all required fields');
            return;
        }

        // Show loading state
        const saveButton = document.querySelector('#servicePackageModal .btn-primary');
        if (saveButton) {
            saveButton.disabled = true;
            saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        }

        fetch('/api/service-packages', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('servicePackageModal'));
                if (modal) {
                    modal.hide();
                }

                // Show success message
                showToast('Service package created successfully!', 'success');

                // Reload the page to show new package
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showToast('Error: ' + (data.message || 'Failed to create service package'), 'error');
            }
        })
        .catch(error => {
            console.error('Error submitting service package:', error);
            showToast('Error creating service package. Please try again.', 'error');
        })
        .finally(() => {
            // Reset button state
            if (saveButton) {
                saveButton.disabled = false;
                saveButton.innerHTML = 'Save Package';
            }
        });

    } catch (error) {
        console.error('Service form submission error:', error);
        showToast('Error submitting form. Please try again.', 'error');
    }
}

function loadCustomersForPrepaid() {
    return fetch('/packages/api/customers?q=')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const select = document.getElementById('apCustomer');
                select.innerHTML = '<option value="">Search / select customer...</option>';

                data.customers.forEach(customer => {
                    const option = document.createElement('option');
                    option.value = customer.id;
                    option.textContent = `${customer.name} - ${customer.phone || 'No phone'}`;
                    select.appendChild(option);
                });
            }
        });
}

// Load services for prepaid modal  
function loadServicesForPrepaid() {
    return fetch('/packages/api/services')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const select = document.getElementById('apService');
                select.innerHTML = '<option value="">Choose a service...</option>';

                data.services.forEach(service => {
                    const option = document.createElement('option');
                    option.value = service.id;
                    option.textContent = `${service.name} - ₹${service.price}`;
                    select.appendChild(option);
                });
            }
        });
}

// Validate prepaid form and enable/disable save buttonon
function validatePrepaidForm() {
    const customer = document.getElementById('apCustomer').value;
    const service = document.getElementById('apService').value;
    const pricePaid = parseFloat(document.getElementById('apPricePaid').value) || 0;

    const isValid = customer && service && pricePaid >= 0;

    const saveBtn = document.getElementById('apSave');
    saveBtn.disabled = !isValid;

    // Update summary if valid
    if (isValid) {
        updatePrepaidSummary();
    } else {
        document.getElementById('apSummary').style.display = 'none';
    }
}

// Update prepaid assignment summary
function updatePrepaidSummary() {
    const payAmount = parseFloat(document.getElementById('apPayAmount').value) || 0;
    const getValue = parseFloat(document.getElementById('apGetValue').value) || 0;
    const pricePaid = parseFloat(document.getElementById('apPricePaid').value) || 0;
    const validity = document.getElementById('apValidity').value || 0;

    // Calculate actual benefit based on price paid
    const actualBenefit = pricePaid > 0 ? ((getValue - pricePaid) / pricePaid * 100) : 0;

    const summaryContent = `
        <div class="row">
            <div class="col-md-6">
                <strong>Pay:</strong> ₹${pricePaid.toFixed(2)} → 
                <strong>Get value:</strong> ₹${getValue.toFixed(2)}
            </div>
            <div class="col-md-6">
                <strong>Benefit:</strong> ${actualBenefit.toFixed(1)}% • 
                <strong>Validity:</strong> ${validity} months
            </div>
        </div>
    `;

    document.getElementById('apSummaryContent').innerHTML = summaryContent;
    document.getElementById('apSummary').style.display = 'block';
}

// Save prepaid assignment
function savePrepaidAssignment() {
    const templateId = document.getElementById('apTemplateId').value;
    const customerId = document.getElementById('apCustomer').value;
    const serviceId = document.getElementById('apService').value;
    const pricePaid = parseFloat(document.getElementById('apPricePaid').value);
    const expiresOn = document.getElementById('apExpiresOn').value || null;
    const notes = document.getElementById('apNotes').value || '';

    if (!templateId || !customerId || !serviceId || pricePaid < 0) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    // Show loading state
    const saveBtn = document.getElementById('apSave');
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';

    const assignmentData = {
        package_type: 'prepaid',
        package_id: templateId,
        customer_id: customerId,
        service_id: serviceId,
        price_paid: pricePaid,
        expires_on: expiresOn,
        notes: notes
    };

    fetch('/packages/api/assign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(assignmentData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(`✅ Assigned '${document.getElementById('apTemplateName').value}' to ${document.getElementById('apCustomer').selectedOptions[0]?.textContent.split(' - ')[0] || 'customer'}`, 'success');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignPrepaidModal'));
            modal.hide();

            // Refresh packages table if it exists
            if (typeof loadPackages === 'function') {
                loadPackages();
            }

            // Refresh page as fallback
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        } else {
            throw new Error(data.error || 'Assignment failed');
        }
    })
    .catch(error => {
        console.error('Error assigning package:', error);
        showToast('Error assigning package: ' + error.message, 'error');
    })
    .finally(() => {
        // Restore button state
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    });
}

// Setup prepaid form event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Form validation events
    const prepaidForm = document.getElementById('assignPrepaidForm');
    if (prepaidForm) {
        prepaidForm.addEventListener('input', validatePrepaidForm);
        prepaidForm.addEventListener('change', validatePrepaidForm);
    }

    // Price paid changes trigger benefit recalculation
    const pricePaidInput = document.getElementById('apPricePaid');
    if (pricePaidInput) {
        pricePaidInput.addEventListener('input', () => {
            validatePrepaidForm();
            updatePrepaidSummary();
        });
    }

    // Edit pay amount toggle
    const editPayAmountBtn = document.getElementById('editPayAmount');
    if (editPayAmountBtn) {
        editPayAmountBtn.addEventListener('click', () => {
            const payAmountInput = document.getElementById('apPayAmount');
            if (payAmountInput.hasAttribute('readonly')) {
                payAmountInput.removeAttribute('readonly');
                payAmountInput.focus();
                editPayAmountBtn.innerHTML = '<i class="fas fa-save"></i>';
                editPayAmountBtn.title = 'Save Pay Amount';
            } else {
                payAmountInput.setAttribute('readonly', true);
                editPayAmountBtn.innerHTML = '<i class="fas fa-edit"></i>';
                editPayAmountBtn.title = 'Edit Pay Amount';

                // Update price paid to match pay amount if not manually set
                const pricePaidInput = document.getElementById('apPricePaid');
                if (!pricePaidInput.value || pricePaidInput.value == payAmountInput.value) {
                    pricePaidInput.value = payAmountInput.value;
                }

                validatePrepaidForm();
            }
        });
    }
});

// Assign from template function (existing functionality)
function assignFromTemplate(templateId, packageType) {
    console.log('Assigning from template:', templateId, packageType);

    // Find the button to get package data
    const button = document.querySelector(`[data-template-id="${templateId}"]`);
    if (!button) {
        showToast('Package data not found', 'error');
        return;
    }

    const packageName = button.dataset.packageName;
    const packagePrice = button.dataset.packagePrice;

    // Open the assign modal with pre-filled data
    openAssignPackageModal(templateId, packageName, packageType, packagePrice);
}

// Expose functions to global scope
window.PackagesUI.assignFromTemplate = assignFromTemplate;
window.PackagesUI.assignPrepaidFromTemplate = assignPrepaidFromTemplate;

/**
 * View assignment details modal
 */
async function viewAssignmentDetails(assignmentId) {
    try {
        const response = await fetch(`/packages/api/view-assignment-details/${assignmentId}`);
        const data = await response.json();

        if (data.success) {
            // Create and show modal with the returned HTML
            const modalHtml = `
                <div class="modal fade" id="viewAssignmentModal" tabindex="-1" data-bs-backdrop="static">
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            ${data.html}
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal if any
            const existingModal = document.getElementById('viewAssignmentModal');
            if (existingModal) {
                existingModal.remove();
            }

            // Add new modal to body
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('viewAssignmentModal'));
            modal.show();

            // Remove modal from DOM when hidden
            modal._element.addEventListener('hidden.bs.modal', () => {
                modal._element.remove();
            });
        } else {
            showToast(data.error || 'Error loading assignment details', 'error');
        }
    } catch (error) {
        console.error('Error viewing assignment details:', error);
        showToast('Error loading assignment details', 'error');
    }
}

/**
 * View customer details modal  
 */
async function viewCustomerDetails(customerId) {
    try {
        const response = await fetch(`/packages/api/customers/${customerId}`);
        const data = await response.json();

        if (data.success && data.customer) {
            const customer = data.customer;

            // Create modal HTML
            const modalHtml = `
                <div class="modal fade" id="viewCustomerModal" tabindex="-1" data-bs-backdrop="static">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">
                                    <i class="fas fa-user text-primary me-2"></i>Customer Details
                                </h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>Name:</strong><br>
                                        ${customer.name}
                                    </div>
                                    <div class="col-md-6">
                                        <strong>Phone:</strong><br>
                                        ${customer.phone || 'N/A'}
                                    </div>
                                </div>
                                <div class="row mb-3">
                                    <div class="col-md-6">
                                        <strong>Email:</strong><br>
                                        ${customer.email || 'N/A'}
                                    </div>
                                    <div class="col-md-6">
                                        <strong>Member Since:</strong><br>
                                        ${customer.created_at || 'N/A'}
                                    </div>
                                </div>
                                ${customer.address ? `
                                <div class="row mb-3">
                                    <div class="col-12">
                                        <strong>Address:</strong><br>
                                        ${customer.address}
                                    </div>
                                </div>
                                ` : ''}
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Remove existing modal if any
            const existingModal = document.getElementById('viewCustomerModal');
            if (existingModal) {
                existingModal.remove();
            }

            // Add new modal to body
            document.body.insertAdjacentHTML('beforeend', modalHtml);

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('viewCustomerModal'));
            modal.show();

            // Remove modal from DOM when hidden
            modal._element.addEventListener('hidden.bs.modal', () => {
                modal._element.remove();
            });
        } else {
            showToast(data.error || 'Error loading customer details', 'error');
        }
    } catch (error) {
        console.error('Error viewing customer details:', error);
        showToast('Error loading customer details', 'error');
    }
}

// Add missing global functions
window.viewAssignmentDetails = viewAssignmentDetails;
window.viewCustomerDetails = viewCustomerDetails;

// Make these functions available for yearly package assignments
window.openAssignSimple = openAssignSimple;
window.saveAssignSimple = saveAssignSimple;
window.viewAssignedCustomers = viewAssignedCustomers;


/**
 * Show package preview when template is selected
 */
function showPackagePreview() {
    const select = document.getElementById('assignPackage');
    const preview = document.getElementById('packagePreview');
    const itemsContainer = document.getElementById('packageItems');
    const priceInput = document.getElementById('assignPrice');
    const assignServiceSelection = document.getElementById('assign_service_selection');
    const assignPackageTypeInput = document.getElementById('assign_package_type');

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

        // Handle service package assignment
        if (template.type === 'service_package') {
            assignServiceSelection.style.display = 'block';
            assignPackageTypeInput.value = 'service_package';
        } else {
            assignServiceSelection.style.display = 'none';
            assignPackageTypeInput.value = 'prepaid';
        }

    } else {
        preview.style.display = 'none';
        priceInput.value = '';
        assignServiceSelection.style.display = 'none';
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
    const assignServiceId = document.getElementById('assign_service_id').value;
    const packageType = document.getElementById('assign_package_type').value; // Get the actual package type

    let isValid = customer && package && price && parseFloat(price) > 0;

    // If it's a service package and the service selection is visible, service ID is required
    if (document.getElementById('assign_service_selection').style.display !== 'none' && packageType === 'service_package') {
        isValid = isValid && assignServiceId;
    }

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

        // Add service_id if it's a service package and selected
        if (document.getElementById('assign_service_selection').style.display !== 'none' && document.getElementById('assign_package_type').value === 'service_package') {
            formData.service_id = parseInt(document.getElementById('assign_service_id').value);
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
            const packageName = document.getElementById('assign_package_name').value;
            const customerSelect = document.getElementById('assign_customer_id');
            const customerName = customerSelect.selectedOptions[0]?.text.split(' - ')[0] || 'customer';

            let successMessage = `✅ "${packageName}" assigned to ${customerName}`;
            if (formData.service_id) {
                const serviceName = document.getElementById('assign_service_id').selectedOptions[0]?.text.split(' - ')[0];
                successMessage = `✅ "${packageName}" assigned for ${serviceName} to ${customerName}`;
            }

            showToast(successMessage, 'success');
            bootstrap.Modal.getInstance(document.getElementById('assignPackageModal')).hide();

            // Refresh the page to show updated assignments
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Error: ' + (data.message || data.error), 'error');
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
        // Create a simple Bootstrap toast
        const toastContainer = document.getElementById('toast-container') || createToastContainer();

        const toastId = 'toast-' + Date.now();
        const bgClass = {
            'success': 'bg-success',
            'error': 'bg-danger', 
            'warning': 'bg-warning',
            'info': 'bg-info'
        }[type] || 'bg-info';

        const toastHtml = `
            <div id="${toastId}" class="toast ${bgClass} text-white" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header ${bgClass} text-white border-0">
                    <strong class="me-auto">Notification</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);

        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement, { delay: 5000 });
        bsToast.show();

        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
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

/**
 * Handle the assignment confirmation after template selection
 */
function confirmPackageAssignment() {
    const form = document.getElementById('assignPackageForm');
    const formData = new FormData(form);

    // Validate required fields
    const customerId = document.getElementById('assign_customer_id').value;
    const packageType = document.getElementById('assign_package_type').value; // Get the actual package type from the hidden input
    const serviceSelectionVisible = document.getElementById('assign_service_selection').style.display !== 'none';

    if (!customerId) {
        document.getElementById('assign_customer_id').classList.add('is-invalid');
        showToast('Please select a customer', 'error');
        return;
    }
    document.getElementById('assign_customer_id').classList.remove('is-invalid');

    // Check service selection for service packages
    if (serviceSelectionVisible && packageType === 'service_package') {
        const serviceId = document.getElementById('assign_service_id').value;
        if (!serviceId) {
            document.getElementById('assign_service_id').classList.add('is-invalid');
            showToast('Please select a service for this package', 'error');
            return;
        }
        document.getElementById('assign_service_id').classList.remove('is-invalid');
    }

    // Disable button during submission
    const submitButton = document.getElementById('saveAssignPackage'); // Corrected button ID
    const originalText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';

    const data = {};
    formData.forEach((value, key) => {
        // Ensure we don't send empty values if they are not required or handled
        if (value !== '' && value !== null) {
            data[key] = value;
        }
    });

    // Manually add service_id if it's a service package and selected
    if (serviceSelectionVisible && packageType === 'service_package') {
        data.service_id = document.getElementById('assign_service_id').value;
    }

    fetch('/packages/api/assign', { // Corrected API endpoint
        method: 'POST',
        headers: {
            'Content-Type': 'application/json', // Use JSON for body
        },
        body: JSON.stringify(data) // Stringify the data object
    })
    .then(response => response.json())
    .then(data => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;

        if (data.success) {
            const serviceName = serviceSelectionVisible ?
                document.getElementById('assign_service_id').selectedOptions[0]?.text.split(' - ')[0] : '';
            const successMessage = serviceName ?
                `✅ "${data.package_name}" assigned for ${serviceName} to ${data.customer_name}` :
                `✅ "${data.package_name}" assigned to ${data.customer_name}`;

            showToast(successMessage, 'success');
            bootstrap.Modal.getInstance(document.getElementById('assignPackageModal')).hide();
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Error: ' + (data.message || data.error), 'error');
        }
    })
    .catch(error => {
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
        console.error('Error:', error);
        showToast('An error occurred while assigning the package.', 'error');
    });
}


// Event delegation for assign buttons
document.addEventListener('click', function(e) {
    if (e.target.closest('[data-action="assign"]')) {
        const btn = e.target.closest('[data-action="assign"]');
        e.preventDefault();
        e.stopPropagation();

        const templateId = btn.dataset.templateId;
        const packageType = btn.dataset.packageType || 'prepaid';

        if (templateId) {
            window.PackagesUI.assignFromTemplate(templateId, packageType);
        }
    }
});

// Keyboard support for assign buttons
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        const btn = e.target.closest('[data-action="assign"]');
        if (btn) {
            e.preventDefault();
            btn.click();
        }
    }
});

// ========================================
// STUDENT OFFER MANAGEMENT
// ========================================

// Load student offers packages
async function loadStudentPackages() {
    try {
        console.log('Loading student packages specifically for student tab only');

        const response = await fetch('/api/student-offers');
        const data = await response.json();

        const tableBody = document.querySelector('#tblStudentOffers tbody');
        if (!tableBody) {
            console.error('Student offers table body not found');
            return;
        }

        tableBody.innerHTML = '';

        if (data && data.length > 0) {
            data.forEach(offer => {
                const row = document.createElement('tr');
                const servicesList = offer.services ? offer.services.map(s => s.name).join(', ') : 'No services';
                const validPeriod = `${offer.valid_from} to ${offer.valid_to}`;

                row.innerHTML = `
                    <td><small>${servicesList}</small></td>
                    <td>₹${offer.services ? offer.services.reduce((total, s) => total + s.price, 0).toFixed(2) : '0.00'}</td>
                    <td><strong>${offer.discount_percentage}%</strong></td>
                    <td>₹${offer.services ? (offer.services.reduce((total, s) => total + s.price, 0) * (1 - offer.discount_percentage / 100)).toFixed(2) : '0.00'}</td>
                    <td>₹${offer.services ? (offer.services.reduce((total, s) => total + s.price, 0) * (offer.discount_percentage / 100)).toFixed(2) : '0.00'}</td>
                    <td>${offer.valid_days}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-success btn-sm"
                                    onclick="openAssignSimple(${offer.id}, 'student')"
                                    title="Assign to Customer"
                                    data-action="assign-simple"
                                    data-template-id="${offer.id}"
                                    data-package-type="student">
                                <i class="fas fa-user-plus"></i> Assign
                            </button>
                            <button class="btn btn-outline-primary" onclick="editStudentOffer(${offer.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteStudentOffer(${offer.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // Update count
            const countElement = document.getElementById('student-total-count');
            if (countElement) {
                countElement.textContent = data.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No student offers found
                    </td>
                </tr>
            `;
        }

        console.log(`Successfully loaded ${data.length || 0} student offers`);

    } catch (error) {
        console.error('Error loading student offers:', error);
        showToast('Error loading student offers', 'error');
    }
}

/**
 * Delete student offer with confirmation
 */
async function deleteStudentOffer(offerId) {
    if (!confirm('Are you sure you want to delete this student offer?')) {
        return;
    }

    try {
        const response = await fetch(`/api/student-offers/${offerId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success || response.ok) {
            showToast('Student offer deleted successfully!', 'success');
            await loadStudentPackages();
        } else {
            throw new Error(result.error || 'Failed to delete student offer');
        }
    } catch (error) {
        console.error('Error deleting student offer:', error);
        showToast('Error deleting student offer: ' + error.message, 'error');
    }
}

/**
 * Edit student offer function
 */
function editStudentOffer(offerId) {
    if (typeof loadStudentOfferForEdit === 'function') {
        loadStudentOfferForEdit(offerId);
    } else {
        console.log('Edit student offer:', offerId);
        // Fallback to basic alert
        alert('Edit functionality will be available soon');
    }
} ${offer.valid_to}`;

                row.innerHTML = `
                    <td><strong>${offer.discount_percentage}%</strong></td>
                    <td><small>${servicesList}</small></td>
                    <td>${offer.valid_days}</td>
                    <td><small>${validPeriod}</small></td>
                    <td><small>${offer.conditions}</small></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="editStudentOffer(${offer.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteStudentOffer(${offer.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-primary" onclick="assignStudentOffer(${offer.id})" title="Assign">
                                <i class="fas fa-user-plus"></i>
                            </button>
                        </div>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // Update count
            const countElement = document.getElementById('student-total-count');
            if (countElement) {
                countElement.textContent = data.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No student offers found
                    </td>
                </tr>
            `;
        }

        console.log(`Successfully loaded ${data.length || 0} student offers`);

    } catch (error) {
        console.error('Error loading student offers:', error);
        showToast('Error loading student offers', 'error');
    }
}

// Initialize student offer modals
function initializeStudentOfferModals() {
    // Load services into dropdowns
    loadServicesForStudentOffers();

    // Set default dates (today and 6 months from now)
    const today = new Date().toISOString().split('T')[0];
    const sixMonthsLater = new Date();
    sixMonthsLater.setMonth(sixMonthsLater.getMonth() + 6);
    const futureDate = sixMonthsLater.toISOString().split('T')[0];

    const validFromField = document.querySelector('input[name="valid_from"]');
    const validToField = document.querySelector('input[name="valid_to"]');
    
    if (validFromField) validFromField.value = today;
    if (validToField) validToField.value = futureDate;

    // Form validation event listeners
    const addForm = document.getElementById('addStudentOfferForm');
    if (addForm) {
        addForm.addEventListener('input', validateStudentOfferForm);
        addForm.addEventListener('change', validateStudentOfferForm);
        
        // Initial validation to set correct button state
        validateStudentOfferForm();
    }

    // Valid days dropdown change handler
    const validDaysSelect = document.querySelector('select[name="valid_days"]');
    if (validDaysSelect) {
        validDaysSelect.addEventListener('change', function() {
            const customDiv = document.getElementById('customValidDaysDiv');
            if (this.value === 'Custom') {
                customDiv.style.display = 'block';
            } else {
                customDiv.style.display = 'none';
            }
        });
    }

    // Edit form valid days handler
    const editValidDaysSelect = document.getElementById('editStudentValidDays');
    if (editValidDaysSelect) {
        editValidDaysSelect.addEventListener('change', function() {
            const editCustomDiv = document.getElementById('editCustomValidDaysDiv');
            if (this.value === 'Custom') {
                editCustomDiv.style.display = 'block';
            } else {
                editCustomDiv.style.display = 'none';
            }
        });
    }

    // Save button event listener
    const saveBtn = document.getElementById('saveStudentOfferBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveStudentOffer);
    }

    // Update button event listener
    const updateBtn = document.getElementById('updateStudentOffer');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateStudentOffer);
    }
}

// Load services for student offer dropdowns
async function loadServicesForStudentOffers() {
    try {
        const response = await fetch('/packages/api/services');
        const data = await response.json();

        if (data.success) {
            const addSelect = document.getElementById('serviceIds');
            const editSelect = document.getElementById('editServiceIds');

            const optionsHTML = data.services.map(service => 
                `<option value="${service.id}">${service.name} - ₹${service.price}</option>`
            ).join('');

            if (addSelect) addSelect.innerHTML = optionsHTML;
            if (editSelect) editSelect.innerHTML = optionsHTML;
        }
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

// Validate student offer form
function validateStudentOfferForm() {
    const services = document.getElementById('serviceIds');
    const discount = document.getElementById('discountPercentage');
    const validFrom = document.querySelector('input[name="valid_from"]');
    const validTo = document.querySelector('input[name="valid_to"]');
    const saveBtn = document.getElementById('saveStudentOfferBtn');

    // Check all required fields
    const isValid = services && services.selectedOptions.length > 0 && 
                   discount && discount.value && parseFloat(discount.value) >= 1 && parseFloat(discount.value) <= 100 &&
                   validFrom && validFrom.value && validTo && validTo.value && 
                   new Date(validTo.value) > new Date(validFrom.value);

    if (saveBtn) {
        saveBtn.disabled = !isValid;
    }

    // Update preview
    updateStudentOfferPreview();
}

// Update student offer preview
function updateStudentOfferPreview() {
    const services = document.getElementById('serviceIds');
    const discount = document.getElementById('discountPercentage');
    const validDays = document.querySelector('select[name="valid_days"]');
    const validFrom = document.querySelector('input[name="valid_from"]');
    const validTo = document.querySelector('input[name="valid_to"]');
    const preview = document.getElementById('studentOfferPreview');

    if (services.selectedOptions.length > 0 && discount.value) {
        const selectedServices = Array.from(services.selectedOptions).map(s => s.textContent);
        const previewHTML = `
            <div class="row">
                <div class="col-md-6">
                    <strong>Services:</strong><br>
                    <ul class="mb-2">
                        ${selectedServices.map(s => `<li class="small">${s}</li>`).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <strong>Discount:</strong> ${discount.value}%<br>
                    <strong>Valid:</strong> ${validDays.value}<br>
                    <strong>Period:</strong> ${validFrom.value} to ${validTo.value}
                </div>
            </div>
        `;
        preview.innerHTML = previewHTML;
    } else {
        preview.innerHTML = '<p class="text-muted">Select services and discount to see preview</p>';
    }
}

// Save student offer
async function saveStudentOffer() {
    try {
        const form = document.getElementById('addStudentOfferForm');
        if (!form) {
            console.error('Student offer form not found');
            return;
        }

        // Get the save button for loading state
        const saveBtn = document.getElementById('saveStudentOfferBtn');
        if (!saveBtn) {
            console.error('Save button not found');
            return;
        }
        const originalText = saveBtn.innerHTML;
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';

        // Client-side validation
        const services = form.querySelectorAll('input[name="service_ids"]:checked');
        const discountInput = form.querySelector('input[name="discount_percentage"]');
        const validFromInput = form.querySelector('input[name="valid_from"]');
        const validToInput = form.querySelector('input[name="valid_to"]');

        // Validate at least one service selected
        if (services.length === 0) {
            throw new Error('Please select at least one service');
        }

        // Validate discount percentage
        const discount = parseFloat(discountInput.value);
        if (!discount || discount < 1 || discount > 100) {
            throw new Error('Discount percentage must be between 1 and 100');
        }

        // Validate dates
        if (!validFromInput.value || !validToInput.value) {
            throw new Error('Please select both valid from and to dates');
        }

        const validFrom = new Date(validFromInput.value);
        const validTo = new Date(validToInput.value);
        if (validTo < validFrom) {
            throw new Error('Valid To Date must be greater than or equal to Valid From Date');
        }

        const formData = new FormData(form);

        // Handle valid days
        const validDaysSelect = form.querySelector('select[name="valid_days"]');
        const customValidDays = form.querySelector('input[name="custom_valid_days"]');
        if (validDaysSelect && validDaysSelect.value === 'Custom' && customValidDays && customValidDays.value) {
            formData.set('valid_days', customValidDays.value);
        }

        // Convert to JSON
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'service_ids') {
                if (!data[key]) data[key] = [];
                data[key].push(parseInt(value));
            } else {
                data[key] = value;
            }
        });

        console.log('Submitting student offer data:', data);

        const response = await fetch('/api/student-offers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success === true) {
            showToast('Student offer created successfully!', 'success');

            // Close modal if it exists
            const modal = document.getElementById('addStudentOfferModal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }

            // Reset form
            form.reset();
            
            // Reload table if function exists
            if (typeof loadStudentPackages === 'function') {
                await loadStudentPackages();
            }

            // If on dedicated page, redirect back to packages
            if (window.location.pathname.includes('/add')) {
                window.location.href = '/packages#assign-student';
            }
        } else {
            throw new Error(result.error || 'Failed to create student offer');
        }
    } catch (error) {
        console.error('Error saving student offer:', error);
        // Display server error message or generic error
        const errorMessage = error.message || 'An unexpected error occurred';
        showToast('Error creating student offer: ' + errorMessage, 'error');
    } finally {
        // Always restore button state
        const saveBtn = document.getElementById('saveStudentOfferBtn');
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Student Offer';
        }
    }
}

// Edit student offer - load data and populate form
async function editStudentOffer(offerId) {
    try {
        // Fetch specific offer data
        const response = await fetch(`/api/student-offers/${offerId}`);
        const result = await response.json();

        if (result.success && result.offer) {
            const offer = result.offer;
            
            // Populate edit form fields
            const editForm = document.getElementById('editStudentOfferForm');
            if (!editForm) {
                console.error('Edit form not found');
                return;
            }

            // Set basic fields
            const offerIdField = document.getElementById('editOfferId');
            const discountField = document.getElementById('editStudentDiscountPercentage');
            const validDaysField = document.getElementById('editStudentValidDays');
            const validFromField = document.getElementById('editStudentValidFrom');
            const validToField = document.getElementById('editStudentValidTo');
            const conditionsField = document.getElementById('editStudentConditions');

            if (offerIdField) offerIdField.value = offer.id;
            if (discountField) discountField.value = offer.discount_percentage;
            if (validDaysField) validDaysField.value = offer.valid_days;
            if (validFromField) validFromField.value = offer.valid_from;
            if (validToField) validToField.value = offer.valid_to;
            if (conditionsField) conditionsField.value = offer.conditions || '';

            // Handle service selection (checkboxes or multi-select)
            const serviceCheckboxes = editForm.querySelectorAll('input[name="service_ids"]');
            const serviceSelect = document.getElementById('editStudentOfferServices');
            
            if (serviceCheckboxes.length > 0) {
                // Handle checkbox-based service selection
                serviceCheckboxes.forEach(checkbox => {
                    checkbox.checked = offer.services.some(s => s.id == checkbox.value);
                });
            } else if (serviceSelect) {
                // Handle multi-select dropdown
                Array.from(serviceSelect.options).forEach(option => {
                    option.selected = offer.services.some(s => s.id == option.value);
                });
            }

            // Handle custom valid days
            if (!['Mon-Fri', 'Mon-Sat', 'All Days', 'Weekends'].includes(offer.valid_days)) {
                if (validDaysField) validDaysField.value = 'Custom';
                const customDiv = document.getElementById('editCustomValidDaysDiv');
                const customField = document.getElementById('editCustomValidDays');
                if (customDiv) customDiv.style.display = 'block';
                if (customField) customField.value = offer.valid_days;
            }

            // Show modal
            const modal = document.getElementById('editStudentOfferModal');
            if (modal) {
                const modalInstance = new bootstrap.Modal(modal);
                modalInstance.show();
            }
        } else {
            throw new Error(result.error || 'Student offer not found');
        }
    } catch (error) {
        console.error('Error loading student offer for edit:', error);
        showToast('Error loading student offer: ' + error.message, 'error');
    }
}

// Update student offer
async function updateStudentOffer() {
    try {
        const form = document.getElementById('editStudentOfferForm');
        if (!form) {
            console.error('Edit student offer form not found');
            return;
        }

        const offerId = document.getElementById('editOfferId').value;
        if (!offerId) {
            throw new Error('Student offer ID not found');
        }

        // Get the update button for loading state
        const updateBtn = document.getElementById('updateStudentOffer');
        if (!updateBtn) {
            console.error('Update button not found');
            return;
        }
        const originalText = updateBtn.innerHTML;
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';

        // Client-side validation
        const services = form.querySelectorAll('input[name="service_ids"]:checked, select[name="service_ids"] option:checked');
        const discountInput = form.querySelector('input[name="discount_percentage"]');
        const validFromInput = form.querySelector('input[name="valid_from"]');
        const validToInput = form.querySelector('input[name="valid_to"]');

        // Validate at least one service selected
        if (services.length === 0) {
            throw new Error('Please select at least one service');
        }

        // Validate discount percentage
        const discount = parseFloat(discountInput.value);
        if (!discount || discount < 1 || discount > 100) {
            throw new Error('Discount percentage must be between 1 and 100');
        }

        // Validate dates
        if (!validFromInput.value || !validToInput.value) {
            throw new Error('Please select both valid from and to dates');
        }

        const validFrom = new Date(validFromInput.value);
        const validTo = new Date(validToInput.value);
        if (validTo < validFrom) {
            throw new Error('Valid To Date must be greater than or equal to Valid From Date');
        }

        const formData = new FormData(form);

        // Handle valid days
        const validDaysSelect = form.querySelector('select[name="valid_days"]');
        const customValidDays = form.querySelector('input[name="custom_valid_days"]');
        if (validDaysSelect && validDaysSelect.value === 'Custom' && customValidDays && customValidDays.value) {
            formData.set('valid_days', customValidDays.value);
        }

        // Convert to JSON
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'service_ids') {
                if (!data[key]) data[key] = [];
                data[key].push(parseInt(value));
            } else {
                data[key] = value;
            }
        });

        console.log('Updating student offer data:', data);

        const response = await fetch(`/api/student-offers/${offerId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success === true) {
            showToast('Student offer updated successfully!', 'success');

            // Close modal if it exists
            const modal = document.getElementById('editStudentOfferModal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }

            // Reload table if function exists
            if (typeof loadStudentPackages === 'function') {
                await loadStudentPackages();
            }

            // If on dedicated page, redirect back to packages
            if (window.location.pathname.includes('/edit')) {
                window.location.href = '/packages#assign-student';
            }
        } else {
            throw new Error(result.error || 'Failed to update student offer');
        }
    } catch (error) {
        console.error('Error updating student offer:', error);
        // Display server error message or generic error
        const errorMessage = error.message || 'An unexpected error occurred';
        showToast('Error updating student offer: ' + errorMessage, 'error');
    } finally {
        // Always restore button state
        const updateBtn = document.getElementById('updateStudentOffer');
        if (updateBtn) {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="fas fa-save me-2"></i>Update Student Offer';
        }
    }
}

// Delete student offer
async function deleteStudentOffer(offerId) {
    if (!confirm('Are you sure you want to delete this student offer?')) {
        return;
    }

    try {
        const response = await fetch(`/api/student-offers/${offerId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success || response.ok) {
            showToast('Student offer deleted successfully!', 'success');
            await loadStudentPackages();
        } else {
            throw new Error(result.error || 'Failed to delete student offer');
        }
    } catch (error) {
        console.error('Error deleting student offer:', error);
        showToast('Error deleting student offer: ' + error.message, 'error');
    }
}

// Assign student offer
function assignStudentOffer(offerId) {
    // Implement assignment logic similar to other package types
    console.log('Assigning student offer:', offerId);
    showToast('Student offer assignment feature coming soon!', 'info');
}

// ========================================
// MINIMAL ASSIGN FLOW FUNCTIONALITY
// ========================================

/**
 * Open minimal assign modal for specific package types
 */
async function openAssignSimple(templateId, packageType) {
    console.log('Opening simple assign modal for:', templateId, packageType);

    try {
        // Get template details
        const response = await fetch(`/packages/api/templates/${templateId}`);
        const result = await response.json();

        if (result.success && result.template) {
            const template = result.template;

            // Fill template name
            document.getElementById('asTemplateName').value = template.name;

            // Set hidden fields
            document.getElementById('asTemplateId').value = templateId;
            document.getElementById('asPackageType').value = packageType;
            document.getElementById('asPricePaid').value = template.price || 0;

            // Load customers into dropdown
            await loadCustomersForSimpleAssign();

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('assignSimpleModal'));
            modal.show();
        } else {
            showToast('Error loading package template', 'error');
        }
    } catch (error) {
        console.error('Error opening simple assign modal:', error);
        showToast('Error loading package details', 'error');
    }
}

/**
 * Open assignment details modal
 */
async function viewAssignmentDetails(assignmentId) {
    try {
        const response = await fetch(`/packages/api/assignments/${assignmentId}`);
        const data = await response.json();

        if (data.success && data.assignment) {
            const assignment = data.assignment;

            // Populate modal fields
            document.getElementById('viewAssignmentId').textContent = assignment.id;
            document.getElementById('viewAssignmentCustomer').textContent = assignment.customer_name;
            document.getElementById('viewAssignmentPackage').textContent = assignment.package_name;
            document.getElementById('viewAssignmentDate').textContent = assignment.assigned_on;
            document.getElementById('viewAssignmentPrice').textContent = formatCurrency(assignment.price_paid);
            document.getElementById('viewAssignmentExpiry').textContent = assignment.expires_on || 'N/A';
            document.getElementById('viewAssignmentStatus').textContent = assignment.status;
            document.getElementById('viewAssignmentNotes').textContent = assignment.notes || 'No notes';

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('viewAssignmentDetailsModal'));
            modal.show();
        } else {
            showToast(data.error || 'Error loading assignment details', 'error');
        }
    } catch (error) {
        console.error('Error viewing assignment details:', error);
        showToast('Error loading assignment details', 'error');
    }
}

/**
 * Open customer details modal
 */
async function viewCustomerDetails(customerId) {
    try {
        const response = await fetch(`/packages/api/customers/${customerId}`);
        const data = await response.json();

        if (data.success && data.customer) {
            const customer = data.customer;

            // Populate modal fields
            document.getElementById('viewCustomerName').textContent = customer.full_name;
            document.getElementById('viewCustomerEmail').textContent = customer.email || 'N/A';
            document.getElementById('viewCustomerPhone').textContent = customer.phone || 'N/A';
            document.getElementById('viewCustomerAddress').textContent = customer.address || 'N/A';
            document.getElementById('viewCustomerJoined').textContent = customer.created_at;

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('viewCustomerDetailsModal'));
            modal.show();
        } else {
            showToast(data.error || 'Error loading customer details', 'error');
        }
    } catch (error) {
        console.error('Error viewing customer details:', error);
        showToast('Error loading customer details', 'error');
    }
}

/**
 * Load customers for simple assign dropdown
 */
async function loadCustomersForSimpleAssign() {
    try {
        const response = await fetch('/packages/api/customers');
        const result = await response.json();

        const customerSelect = document.getElementById('asCustomer');
        customerSelect.innerHTML = '<option value="">Select customer...</option>';

        if (result.success && result.customers) {
            result.customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = customer.full_name;
                customerSelect.appendChild(option);
            });
        }

        // Enable save button when customer is selected
        customerSelect.addEventListener('change', function() {
            const saveBtn = document.getElementById('asSave');
            saveBtn.disabled = !this.value;
        });

    } catch (error) {
        console.error('Error loading customers:', error);
        showToast('Error loading customers', 'error');
    }
}

/**
 * Save simple package assignment
 */
async function saveAssignSimple() {
    console.log('Saving simple package assignment...');

    try {
        const templateId = document.getElementById('asTemplateId').value;
        const packageType = document.getElementById('asPackageType').value;
        const customerId = document.getElementById('asCustomer').value;
        const pricePaid = document.getElementById('asPricePaid').value;

        if (!templateId || !packageType || !customerId) {
            showToast('Please fill all required fields', 'warning');
            return;
        }

        const data = {
            package_type: packageType,
            package_id: templateId,
            customer_id: parseInt(customerId),
            price_paid: parseFloat(pricePaid)
        };

        const response = await fetch('/packages/api/assign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Package assigned successfully!', 'success');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignSimpleModal'));
            modal.hide();

            // Reset form
            document.getElementById('assignSimpleForm').reset();
            document.getElementById('asSave').disabled = true;

            // Refresh current tab table
            await refreshCurrentTabTable();

        } else {
            showToast(result.error || 'Error assigning package', 'error');
        }
    } catch (error) {
        console.error('Error saving package assignment:', error);
        showToast('Error assigning package', 'error');
    }
}

/**
 * Refresh the current tab's table
 */
async function refreshCurrentTabTable() {
    const activeTab = document.querySelector('.tab-pane.active');
    if (activeTab) {
        const tabId = activeTab.id;

        // Determine which table to refresh based on active tab
        if (tabId === 'assign-membership') {
            await loadMembershipPackages();
        } else if (tabId === 'assign-student') {
            await loadStudentPackages();
        } else if (tabId === 'assign-yearly') {
            await loadYearlyPackages();
        } else if (tabId === 'assign-kitty') {
            await loadKittyPackages();
        } else if (tabId === 'all-packages') {
            await loadPackages();
        }
    }
}

/**
 * Load packages for tables
 */
async function loadMembershipPackages() {
    console.log('Loading membership packages specifically for membership tab only');

    // Only load if we're on the membership tab
    const membershipTab = document.getElementById('assign-membership');
    if (!membershipTab || !membershipTab.classList.contains('active')) {
        console.log('Not on membership tab, skipping membership load');
        return;
    }

    await loadPackageTypeIntoTable('membership', 'tblMemberships');
}

async function loadStudentPackages() {
    try {
        console.log('Loading student packages specifically for student tab only');

        const response = await fetch('/api/student-offers');
        const data = await response.json();

        const tableBody = document.querySelector('#tblStudentOffers tbody');
        if (!tableBody) {
            console.error('Student offers table body not found');
            return;
        }

        tableBody.innerHTML = '';

        if (data && data.length > 0) {
            data.forEach(offer => {
                const row = document.createElement('tr');
                const servicesList = offer.services ? offer.services.map(s => s.name).join(', ') : 'No services';
                const validPeriod = `${offer.valid_from} to ${offer.valid_to}`;

                row.innerHTML = `
                    <td><strong>${offer.discount_percentage}%</strong></td>
                    <td><small>${servicesList}</small></td>
                    <td>${offer.valid_days}</td>
                    <td><small>${validPeriod}</small></td>
                    <td><small>${offer.conditions}</small></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="editStudentOffer(${offer.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteStudentOffer(${offer.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-primary" onclick="assignStudentOffer(${offer.id})" title="Assign">
                                <i class="fas fa-user-plus"></i>
                            </button>
                        </div>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // Update count
            const countElement = document.getElementById('student-total-count');
            if (countElement) {
                countElement.textContent = data.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No student offers found
                    </td>
                </tr>
            `;
        }

        console.log(`Successfully loaded ${data.length || 0} student offers`);

    } catch (error) {
        console.error('Error loading student offers:', error);
        showToast('Error loading student offers', 'error');
    }
}

async function loadYearlyPackages() {
    try {
        console.log('Loading yearly packages specifically for yearly tab only');

        const response = await fetch('/api/yearly-memberships');
        const data = await response.json();

        const tableBody = document.querySelector('#tblYearlyMemberships tbody');
        if (!tableBody) {
            console.error('Yearly memberships table body not found');
            return;
        }

        tableBody.innerHTML = '';

        if (data && data.length > 0) {
            data.forEach(pkg => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td><strong>${pkg.name}</strong></td>
                    <td>₹${parseFloat(pkg.price || 0).toLocaleString()}</td>
                    <td>${pkg.validity_months || 'N/A'} months</td>
                    <td>${pkg.discount_percent || 0}%</td>
                    <td>
                        <button class="btn btn-primary btn-sm" 
                                onclick="openAssignSimple(${pkg.id}, 'yearly')" 
                                title="Assign to customer">
                            <i class="fas fa-user-plus"></i> Assign
                        </button>
                    </td>
                `;

                tableBody.appendChild(row);
            });

            // Update count
            const countElement = document.getElementById('yearly-total-count');
            if (countElement) {
                countElement.textContent = data.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No yearly memberships found
                    </td>
                </tr>
            `;
        }

        console.log(`Successfully loaded ${data.length || 0} yearly memberships`);

    } catch (error) {
        console.error('Error loading yearly memberships:', error);
        showToast('Error loading yearly memberships', 'error');
    }
}

async function loadKittyPackages() {
    console.log('Loading kitty packages specifically');
    await loadPackageTypeIntoTable('kitty', 'tblKittyPackages');
}

/**
 * Generic function to load package type into table
 */
async function loadPackageTypeIntoTable(packageType, tableId) {
    try {
        console.log(`Loading ${packageType} packages into ${tableId}`);

        // Check if the target table exists and is visible
        const targetTable = document.getElementById(tableId);
        if (!targetTable) {
            console.log(`Table ${tableId} not found, skipping load`);
            return;
        }

        // Check if we're on the correct tab for this package type
        const tabMap = {
            'tblMemberships': 'assign-membership',
            'tblStudentOffers': 'assign-student', 
            'tblYearlyMemberships': 'assign-yearly',
            'tblKittyPackages': 'assign-kitty'
        };

        const expectedTab = tabMap[tableId];
        if (expectedTab) {
            const tabElement = document.getElementById(expectedTab);
            if (!tabElement || !tabElement.classList.contains('active')) {
                console.log(`Not on correct tab for ${tableId}, skipping load`);
                return;
            }
        }

        // API endpoints for each package type
        const endpoints = {
            membership: '/api/memberships',
            student: '/api/student-offers',
            yearly: '/api/yearly-memberships',
            kitty: '/api/kitty-parties'
        };

        const endpoint = endpoints[packageType];
        if (!endpoint) {
            console.error(`No endpoint defined for package type: ${packageType}`);
            return;
        }

        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const packages = Array.isArray(data) ? data : (data.packages || data);

        // Get the table body element
        const tableBody = document.querySelector(`#${tableId} tbody`);
        if (!tableBody) {
            console.error(`Table body not found for tableId: ${tableId}`);
            return;
        }

        // Clear existing content
        tableBody.innerHTML = '';

        if (!packages || packages.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No ${packageType} packages found
                    </td>
                </tr>
            `;
            return;
        }

        // Populate table with packages
        packages.forEach(pkg => {
            const row = document.createElement('tr');

            // Build services display
            let servicesDisplay = 'No services specified';
            if (pkg.services && pkg.services.length > 0) {
                servicesDisplay = pkg.services.slice(0, 2).map(s => s.name).join(', ');
                if (pkg.services.length > 2) {
                    servicesDisplay += ` +${pkg.services.length - 2} more`;
                }
            } else if (pkg.selected_services && pkg.selected_services.length > 0) {
                servicesDisplay = pkg.selected_services.slice(0, 2).map(s => s.name).join(', ');
                if (pkg.selected_services.length > 2) {
                    servicesDisplay += ` +${pkg.selected_services.length - 2} more`;
                }
            } else if (pkg.services_included) {
                servicesDisplay = pkg.services_included.length > 50 ? 
                    pkg.services_included.substring(0, 50) + '...' : 
                    pkg.services_included;
            }

            if (packageType === 'membership') {
                row.innerHTML = `
                    <td><strong>${pkg.name}</strong></td>
                    <td>₹${parseFloat(pkg.price || 0).toLocaleString()}</td>
                    <td>${pkg.validity_months || 12} months</td>
                    <td>${servicesDisplay}</td>
                    <td>
                        <span class="badge ${pkg.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${pkg.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="openAssignSimple(${pkg.id}, 'membership')" title="Assign">
                            <i class="fas fa-user-plus"></i> Assign
                        </button>
                    </td>
                `;
            } else if (packageType === 'yearly') {
                row.innerHTML = `
                    <td><strong>${pkg.name}</strong></td>
                    <td>₹${parseFloat(pkg.price || 0).toLocaleString()}</td>
                    <td>${pkg.validity_months || 12} months</td>
                    <td>${pkg.discount_percent || 0}%</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="openAssignSimple(${pkg.id}, 'yearly')" title="Assign">
                            <i class="fas fa-user-plus"></i> Assign
                        </button>
                    </td>
                `;
            } else if (packageType === 'kitty') {
                row.innerHTML = `
                    <td><strong>${pkg.name}</strong></td>
                    <td>₹${parseFloat(pkg.price || 0).toLocaleString()}</td>
                    <td>₹${parseFloat(pkg.after_value || 0).toLocaleString()}</td>
                    <td>${pkg.min_guests || 'N/A'}</td>
                    <td>${servicesDisplay}</td>
                    <td>${pkg.valid_from && pkg.valid_to ? `${pkg.valid_from} to ${pkg.valid_to}` : 'No validity period'}</td>
                    <td>${pkg.conditions || 'No conditions'}</td>
                    <td>
                        <span class="badge ${pkg.is_active ? 'bg-success' : 'bg-secondary'}">
                            ${pkg.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="editKittyParty(${pkg.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteKittyParty(${pkg.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-primary" onclick="assignKittyParty(${pkg.id})" title="Assign">
                                <i class="fas fa-user-plus"></i>
                            </button>
                        </div>
                    </td>
                `;
            }

            tableBody.appendChild(row);
        });

        console.log(`Successfully loaded ${packages.length} ${packageType} packages`);

    } catch (error) {
        console.error(`Error loading ${packageType} packages:`, error);

        const tableBody = document.querySelector(`#${tableId} tbody`);
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger py-4">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error loading ${packageType} packages
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * Create table row for package with assign button
 */
function createPackageTableRow(pkg, packageType) {
    const row = document.createElement('tr');

    // Column content based on package type
    if (packageType === 'membership') {
        row.innerHTML = `
            <td><strong>${pkg.name}</strong></td>
            <td>₹${pkg.price}</td>
            <td>${pkg.validity_months} months</td>
            <td>${pkg.description || 'No description'}</td>
            <td>
                <button class="btn btn-primary btn-sm"
                        title="Assign to customer"
                        data-action="assign-simple"
                        data-template-id="${pkg.id}"
                        data-package-type="membership">
                    <i class="fas fa-user-plus"></i>
                </button>
            </td>
        `;
    } else if (packageType === 'student') {
        row.innerHTML = `
            <td><strong>${pkg.name}</strong></td>
            <td>₹${pkg.actual_price}</td>
            <td>₹${pkg.after_price}</td>
            <td>${pkg.description || 'No description'}</td>
            <td>
                <button class="btn btn-primary btn-sm"
                        title="Assign to customer"
                        data-action="assign-simple"
                        data-template-id="${pkg.id}"
                        data-package-type="student">
                    <i class="fas fa-user-plus"></i>
                </button>
            </td>
        `;
    } else if (packageType === 'yearly') {
        row.innerHTML = `
            <td><strong>${pkg.name}</strong></td>
            <td>₹${pkg.price}</td>
            <td>${pkg.validity_months} months</td>
            <td>${pkg.discount_percent}%</td>
            <td>
                <button class="btn btn-primary btn-sm"
                        title="Assign to customer"
                        data-action="assign-simple"
                        data-template-id="${pkg.id}"
                        data-package-type="yearly">
                    <i class="fas fa-user-plus"></i>
                </button>
            </td>
        `;
    } else if (packageType === 'kitty') {
        row.innerHTML = `
            <td><strong>${pkg.name}</strong></td>
            <td>₹${pkg.price}</td>
            <td>${pkg.min_guests}</td>
            <td>${pkg.description || 'No description'}</td>
            <td>
                <button class="btn btn-primary btn-sm"
                        title="Assign to customer"
                        data-action="assign-simple"
                        data-template-id="${pkg.id}"
                        data-package-type="kitty">
                    <i class="fas fa-user-plus"></i>
                </button>
            </td>
        `;
    }

    return row;
}

// Event delegation for assign buttons - Wait for DOM to be ready
function setupTableEventDelegation() {
    // Event delegation for assign buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-action="assign-simple"]')) {
            const button = e.target.closest('[data-action="assign-simple"]');
            const templateId = button.getAttribute('data-template-id');
            const packageType = button.getAttribute('data-package-type');
            openAssignSimple(templateId, packageType);
        }
    });

    // Save button event listener for simple assign modal
    const saveBtn = document.getElementById('asSave');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveAssignSimple);
    }
}

// Expose functions to global scope
window.loadMembershipPackages = loadMembershipPackages;
window.loadStudentPackages = loadStudentPackages;
window.loadYearlyPackages = loadYearlyPackages;
window.loadKittyPackages = loadKittyPackages;
window.openAssignSimple = openAssignSimple;
window.saveAssignSimple = saveAssignSimple;

// Kitty party functions
window.loadKittyPackages = loadKittyPackages;
window.editKittyParty = editKittyParty;
window.deleteKittyParty = deleteKittyParty;
window.assignKittyParty = assignKittyParty;


// Load kitty packages for tables
async function loadKittyPackages() {
    try {
        console.log('Loading kitty party packages...');

        const response = await fetch('/api/kitty-parties');
        const data = await response.json();

        if (data.success && data.parties) {
            const tableBody = document.querySelector('#tblKittyPackages tbody');
            tableBody.innerHTML = '';

            data.parties.forEach(party => {
                const row = document.createElement('tr');
                // Display linked services from kittyparty_services relationship
                const servicesList = party.services && party.services.length > 0 ? 
                    party.services.map(s => s.name).join(', ') : 'No services selected';
                const validPeriod = party.valid_from && party.valid_to ? 
                    `${party.valid_from} to ${party.valid_to}` : 'No validity period';
                const afterValue = party.after_value ? `₹${party.after_value}` : 'N/A';
                const conditions = party.conditions || 'No conditions';
                const statusBadge = party.is_active ? 
                    '<span class="badge bg-success">Active</span>' : 
                    '<span class="badge bg-secondary">Inactive</span>';

                row.innerHTML = `
                    <td><strong>${party.name}</strong></td>
                    <td>₹${party.price}</td>
                    <td>${afterValue}</td>
                    <td>${party.min_guests}</td>
                    <td><small>${servicesList}</small></td>
                    <td><small>${validPeriod}</small></td>
                    <td><small>${conditions}</small></td>
                    <td>${statusBadge}</td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="editKittyParty(${party.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteKittyParty(${party.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-primary" onclick="assignKittyParty(${party.id})" title="Assign">
                                <i class="fas fa-user-plus"></i>
                            </button>
                        </div>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // Update count
            document.getElementById('kitty-total-count').textContent = data.parties.length;
        }
    } catch (error) {
        console.error('Error loading kitty party packages:', error);
        showToast('Error loading kitty party packages', 'error');
    }
}

// Initialize kitty party modals
function initializeKittyPartyModals() {
    // Load services into dropdowns
    loadServicesForKittyParties();

    // Set default dates (today and 3 months from now)
    const today = new Date().toISOString().split('T')[0];
    const threeMonthsLater = new Date();
    threeMonthsLater.setMonth(threeMonthsLater.getMonth() + 3);
    const futureDate = threeMonthsLater.toISOString().split('T')[0];

    document.getElementById('kittyValidFrom').value = today;
    document.getElementById('kittyValidTo').value = futureDate;

    // Form validation event listeners
    const addForm = document.getElementById('addKittyPartyForm');
    if (addForm) {
        addForm.addEventListener('input', validateKittyPartyForm);
        addForm.addEventListener('change', validateKittyPartyForm);
    }

    // Save button event listener
    const saveBtn = document.getElementById('saveKittyParty');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveKittyParty);
    }

    // Update button event listener
    const updateBtn = document.getElementById('updateKittyParty');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateKittyParty);
    }
}

// Load services for kitty party dropdowns
async function loadServicesForKittyParties() {
    try {
        const response = await fetch('/packages/api/services');
        const data = await response.json();

        if (data.success) {
            const addSelect = document.getElementById('kittyPartyServices');
            const editSelect = document.getElementById('editKittyPartyServices');

            const optionsHTML = data.services.map(service => 
                `<option value="${service.id}">${service.name} - ₹${service.price}</option>`
            ).join('');

            if (addSelect) {
                addSelect.innerHTML = optionsHTML;
                addSelect.setAttribute('data-placeholder', 'Select services included in this Kitty Party');
            }
            if (editSelect) {
                editSelect.innerHTML = optionsHTML;
                editSelect.setAttribute('data-placeholder', 'Select services included in this Kitty Party');
            }
        }
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

// Validate kitty party form
function validateKittyPartyForm() {
    const name = document.getElementById('kittyPartyName');
    const price = document.getElementById('kittyPrice');
    const minGuests = document.getElementById('kittyMinGuests');
    const services = document.getElementById('kittyPartyServices');
    const saveBtn = document.getElementById('saveKittyParty');

    const isValid = name.value.trim() && 
                   price.value && parseFloat(price.value) > 0 &&
                   minGuests.value && parseInt(minGuests.value) > 0 &&
                   services.selectedOptions.length > 0;

    if (saveBtn) {
        saveBtn.disabled = !isValid;
    }

    // Show/hide validation feedback for services
    if (services.selectedOptions.length === 0) {
        services.classList.add('is-invalid');
    } else {
        services.classList.remove('is-invalid');
    }

    // Update preview
    updateKittyPartyPreview();
}

// Update kitty party preview
function updateKittyPartyPreview() {
    const name = document.getElementById('kittyPartyName');
    const price = document.getElementById('kittyPrice');
    const afterValue = document.getElementById('kittyAfterValue');
    const minGuests = document.getElementById('kittyMinGuests');
    const services = document.getElementById('kittyPartyServices');
    const validFrom = document.getElementById('kittyValidFrom');
    const validTo = document.getElementById('kittyValidTo');
    const preview = document.getElementById('kittyPartyPreview');

    if (name.value && price.value && minGuests.value && services.selectedOptions.length > 0) {
        const selectedServices = Array.from(services.selectedOptions).map(opt => opt.textContent);
        const afterVal = afterValue.value ? `₹${afterValue.value}` : 'Not set';
        const validPeriod = validFrom.value && validTo.value ? 
            `${validFrom.value} to ${validTo.value}` : 'No validity period';

        const previewHTML = `
            <div class="row">
                <div class="col-md-6">
                    <strong>Party:</strong> ${name.value}<br>
                    <strong>Price:</strong> ₹${price.value}<br>
                    <strong>After Value:</strong> ${afterVal}<br>
                    <strong>Min Guests:</strong> ${minGuests.value}
                </div>
                <div class="col-md-6">
                    <strong>Services:</strong><br>
                    <ul class="mb-2">
                        ${selectedServices.map(s => `<li class="small">${s}</li>`).join('')}
                    </ul>
                    <strong>Valid:</strong> ${validPeriod}
                </div>
            </div>
        `;
        preview.innerHTML = previewHTML;
    } else {
        preview.innerHTML = '<p class="text-muted">Fill in party details to see preview</p>';
    }
}

// Save kitty party
function saveKittyParty() {
    console.log('Submitting kitty party form...');

    const form = document.getElementById('addKittyPartyForm');
    if (!form) {
        console.error('Kitty party form not found');
        return;
    }

    // Show loading state
    const submitBtn = document.querySelector('#kittyPartyModal button[type="submit"]') || 
                     document.getElementById('saveKittyPartyBtn') ||
                     event.target.querySelector('button[type="submit"]');

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Creating...';
    }

    const formData = new FormData(form);

    // Convert to JSON
    const data = {};
    formData.forEach((value, key) => {
        if (key === 'service_ids') {
            if (!data[key]) data[key] = [];
            data[key].push(value);
        } else {
            data[key] = value;
        }
    });

    fetch('/api/kitty-parties', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success || response.ok) {
            showToast('Kitty party created successfully!', 'success');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addKittyPartyModal'));
            if (modal) {
                modal.hide();
            }

            // Reset form
            if (form) {
                form.reset();
            }
            if (submitBtn) {
                submitBtn.disabled = true; // Keep disabled until new data is entered
            }

            // Reload table
            loadKittyPackages();
        } else {
            throw new Error(result.error || 'Failed to create kitty party');
        }
    })
    .catch(error => {
        console.error('Error saving kitty party:', error);
        showToast('Error creating kitty party: ' + error.message, 'error');
    })
    .finally(() => {
        // Restore button state if button exists
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-save me-2"></i>Save Kitty Party';
        }
    });
}

// Edit kitty party
async function editKittyParty(partyId) {
    try {
        const response = await fetch(`/api/kitty-parties`);
        const data = await response.json();
        const party = data.parties.find(p => p.id === partyId);

        if (party) {
            // Populate edit form
            document.getElementById('editPartyId').value = party.id;
            document.getElementById('editKittyPartyName').value = party.name;
            document.getElementById('editKittyPrice').value = party.price;
            document.getElementById('editKittyAfterValue').value = party.after_value || '';
            document.getElementById('editKittyMinGuests').value = party.min_guests;
            document.getElementById('editKittyValidFrom').value = party.valid_from || '';
            document.getElementById('editKittyValidTo').value = party.valid_to || '';
            document.getElementById('editKittyConditions').value = party.conditions || '';

            // Select services in multi-select dropdown
            const serviceSelect = document.getElementById('editKittyPartyServices');
            Array.from(serviceSelect.options).forEach(option => {
                option.selected = party.services && party.services.some(s => s.id == option.value);
            });

            // Show modal
            const modal = new bootstrap.Modal(document.getElementById('editKittyPartyModal'));
            modal.show();
        }
    } catch (error) {
        console.error('Error loading kitty party for edit:', error);
        showToast('Error loading kitty party', 'error');
    }
}

// Update kitty party
async function updateKittyParty() {
    try {
        const form = document.getElementById('editKittyPartyForm');
        const formData = new FormData(form);
        const partyId = document.getElementById('editPartyId').value;

        // Convert to JSON with proper service_ids handling
        const data = {};
        formData.forEach((value, key) => {
            if (key === 'service_ids') {
                if (!data[key]) data[key] = [];
                data[key].push(value);
            } else {
                data[key] = value;
            }
        });

        // Handle boolean conversion
        data.is_active = form.querySelector('input[name="is_active"]').checked;

        const response = await fetch(`/api/kitty-parties/${partyId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Kitty party updated successfully!', 'success');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editKittyPartyModal'));
            if (modal) {
                modal.hide();
            }

            // Reload table
            await loadKittyPackages();
        } else {
            throw new Error(result.error || 'Failed to update kitty party');
        }
    } catch (error) {
        console.error('Error updating kitty party:', error);
        showToast('Error updating kitty party: ' + error.message, 'error');
    }
}

// Delete kitty party
async function deleteKittyParty(partyId) {
    if (!confirm('Are you sure you want to delete this kitty party?')) {
        return;
    }

    try {
        const response = await fetch(`/api/kitty-parties/${partyId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success || response.ok) {
            showToast('Kitty party deleted successfully!', 'success');
            await loadKittyPackages();
        } else {
            throw new Error(result.error || 'Failed to delete kitty party');
        }
    } catch (error) {
        console.error('Error deleting kitty party:', error);
        showToast('Error deleting kitty party: ' + error.message, 'error');
    }
}

// Assign kitty party
function assignKittyParty(partyId) {
    openAssignSimple(partyId, 'kitty');
}