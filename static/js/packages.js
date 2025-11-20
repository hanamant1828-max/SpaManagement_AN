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

// Immediately declare global functions to prevent undefined errors
window.openAssignModal = openAssignModal;
window.openAssignSimple = openAssignSimple;
window.saveAssignSimple = saveAssignSimple;
window.assignPackage = assignPackage;
window.assignServicePackage = assignServicePackage;
window.clearFilters = clearFilters;
window.applyFilters = applyFilters;
window.changePage = changePage;
window.openDetails = openDetails;
window.openUseModal = openUseModal;
window.openAdjustModal = openAdjustModal;
window.editStudentOffer = editStudentOffer;
window.deleteStudentOffer = deleteStudentOffer;
window.assignStudentOffer = assignStudentOffer;
window.saveStudentOffer = saveStudentOffer;
window.updateStudentOffer = updateStudentOffer;
window.editKittyParty = editKittyParty;
window.deleteKittyParty = deleteKittyParty;
window.assignKittyParty = assignKittyParty;
window.saveKittyParty = saveKittyParty;
window.updateKittyParty = updateKittyParty;
window.loadMembershipPackages = loadMembershipPackages;
window.loadStudentPackages = loadStudentPackages;
window.loadYearlyPackages = loadYearlyPackages;
window.loadKittyPackages = loadKittyPackages;
window.viewAssignmentDetails = viewAssignmentDetails;
window.viewCustomerDetails = viewCustomerDetails;
window.confirmPackageAssignment = confirmPackageAssignment;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Customer Packages JS loaded');
    initializePackages(); // Event listeners are set up here
    initializeKittyPartyModals();
    initializeStudentOfferModals();
    setupTableEventDelegation();
    console.log('All global functions attached successfully');
});

/**
 * Open assign package modal
 */
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

/**
 * Open simple assignment modal for packages
 */
function openAssignSimple(packageId, packageType) {
    console.log('Opening simple assign modal for:', packageId, packageType);
    
    // Ensure packageType is set correctly
    if (!packageType) {
        console.error('Package type is required');
        showToast('Package type is missing', 'error');
        return;
    }

    // Try to use the existing assignPackageModal first
    let modal = document.getElementById('assignPackageModal');
    if (!modal) {
        console.error('assignPackageModal not found, trying alternative');
        modal = document.getElementById('assignSimpleModal') || document.getElementById('packageAssignmentModal');
        if (!modal) {
            console.error('No assignment modal found');
            showToast('Assignment modal not available', 'error');
            return;
        }
    }

    // Set hidden fields for package info
    const offerTypeInput = document.getElementById('assignOfferType') || document.getElementById('asPackageType');
    const offerRefInput = document.getElementById('assignOfferReferenceId') || document.getElementById('asTemplateId');

    if (offerTypeInput) {
        offerTypeInput.value = packageType;
        console.log('Set package type:', packageType);
    } else {
        console.error('Package type input field not found');
    }
    
    if (offerRefInput) {
        offerRefInput.value = packageId;
        console.log('Set package ID:', packageId);
    } else {
        console.error('Package ID input field not found');
    }

    // Auto-populate price from package data
    if (currentPackages && currentPackages.length > 0) {
        const packageData = currentPackages.find(pkg => pkg.id == packageId);
        if (packageData && packageData.price) {
            const priceInput = document.getElementById('asPricePaid') || document.getElementById('assignPricePaid');
            if (priceInput) {
                priceInput.value = packageData.price;
                console.log('Auto-populated price:', packageData.price);
            }
        }
    }

    // Reset form first
    const form = document.getElementById('assignPackageForm') || document.getElementById('assignSimpleForm');
    if (form) {
        form.reset();
        // Re-set the hidden fields after reset
        if (offerTypeInput) offerTypeInput.value = packageType;
        if (offerRefInput) offerRefInput.value = packageId;
    }

    // Set package name after form reset
    const packageNameField = document.getElementById('asTemplateName');
    if (packageNameField && currentPackages && currentPackages.length > 0) {
        const packageData = currentPackages.find(pkg => pkg.id == packageId);
        if (packageData) {
            packageNameField.value = packageData.name || `Package ${packageId}`;
            // Also set defaultValue to prevent reset from clearing it
            packageNameField.defaultValue = packageData.name || `Package ${packageId}`;
            console.log('Set package name:', packageData.name);
        }
    }

    // Reset and load customer dropdown
    const customerSelect = document.getElementById('assignCustomerSelect') || document.getElementById('asCustomer');
    if (customerSelect) {
        customerSelect.value = '';

        // Remove existing event listeners to avoid duplicates
        customerSelect.removeEventListener('change', handleCustomerSelection);
        customerSelect.addEventListener('change', handleCustomerSelection);
    }

    // Load customers
    loadCustomersForAssignment().then(() => {
        console.log('Customers loaded for assignment');
    });

    // Show modal and set up event listener using Bootstrap modal events
    const modalInstance = new bootstrap.Modal(modal);
    
    // Initialize payment summary when modal opens
    modal.addEventListener('show.bs.modal', function() {
        // Reset payment summary
        updatePaymentSummary();
    });
    
    // Set up event listener when modal is fully shown (reliable timing)
    modal.addEventListener('shown.bs.modal', function() {
        const saveBtn = document.getElementById('asSave') || document.getElementById('confirmAssignBtn');
        
        if (saveBtn && !saveBtn.dataset.assignListener) {
            saveBtn.dataset.assignListener = 'true';
            saveBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                saveAssignSimple();
            });
            
            console.log('Event listener attached to assign button using modal shown event');
            
            // Initially disable the button until customer is selected
            saveBtn.disabled = true;
            
            // Enable button when customer is selected
            const customerSelect = document.getElementById('asCustomer');
            if (customerSelect && customerSelect.value) {
                saveBtn.disabled = false;
            }
        }
    }, { once: true }); // Use once: true to prevent duplicate listeners
    
    modalInstance.show();
}

// Separate function to handle customer selection
function handleCustomerSelection() {
    const saveBtn = document.getElementById('confirmAssignBtn') || document.getElementById('asSave');
    if (saveBtn) {
        saveBtn.disabled = !this.value;
        console.log('Customer selected, save button enabled:', !saveBtn.disabled);
    }

    // Load existing packages for this customer
    if (this.value) {
        fetch(`/packages/api/customer-packages?customer_id=${this.value}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.packages && data.packages.length > 0) {
                    // Show warning about existing packages
                    const warningDiv = document.getElementById('existingPackagesWarning') || createWarningDiv();
                    warningDiv.innerHTML = `
                        <i class="fas fa-info-circle me-2"></i>
                        <strong>Note:</strong> Customer has ${data.packages.length} active package(s)
                    `;
                    warningDiv.style.display = 'block';
                }
            })
            .catch(err => console.error('Error loading customer packages:', err));
    }
}

function createWarningDiv() {
    const div = document.createElement('div');
    div.id = 'existingPackagesWarning';
    div.className = 'alert alert-warning mt-2';
    div.style.display = 'none';
    const form = document.querySelector('#assignPackageForm, #assignSimpleForm');
    if (form) {
        form.appendChild(div);
    }
    return div;
}

/**
 * Save simple assignment
 */
function saveAssignSimple() {
    console.log('*** SAVE ASSIGN SIMPLE FUNCTION CALLED ***');
    console.log('Saving simple assignment...');

    // Try to get values from multiple possible modal implementations
    const templateId = document.getElementById('asTemplateId')?.value || 
                      document.getElementById('assignOfferReferenceId')?.value ||
                      document.getElementById('selectedPackageId')?.value;
    
    const packageType = document.getElementById('asPackageType')?.value || 
                       document.getElementById('assignOfferType')?.value ||
                       document.getElementById('selectedPackageType')?.value ||
                       'membership';
    
    const customerId = document.getElementById('asCustomer')?.value ||
                      document.getElementById('assignCustomerSelect')?.value ||
                      document.getElementById('assignmentCustomer')?.value;
    
    // Get package price from the current package data if not specified
    const priceInput = document.getElementById('asPricePaid')?.value || 
                       document.getElementById('assignPricePaid')?.value ||
                       document.getElementById('assignmentPrice')?.value;
    
    let pricePaid = parseFloat(priceInput);
    
    // If price input is empty or NaN (but not 0), try to get default from package data
    if (isNaN(pricePaid) && currentPackages && currentPackages.length > 0) {
        const packageData = currentPackages.find(pkg => pkg.id == templateId);
        if (packageData && packageData.price) {
            pricePaid = parseFloat(packageData.price);
            console.log('Using package default price:', pricePaid);
        }
    }
    
    // Fallback to 0 if still no valid price (preserves intentional 0 values)
    if (isNaN(pricePaid)) {
        pricePaid = 0;
    }
    
    const notes = document.getElementById('asNotes')?.value || 
                 document.getElementById('assignNotes')?.value ||
                 document.getElementById('assignmentNotes')?.value || '';

    console.log('Simple assignment data:', {
        templateId,
        packageType,
        customerId,
        pricePaid,
        notes
    });

    if (!templateId || !customerId) {
        showToast('Please select a customer and package', 'warning');
        return;
    }

    const saveBtn = document.getElementById('asSave') ||
                   document.getElementById('confirmAssignBtn') ||
                   document.getElementById('savePackageAssignment') ||
                   document.querySelector('.btn-primary[onclick*="assign"]') ||
                   document.querySelector('#assignPackageModal .btn-primary');
    
    const originalText = saveBtn?.innerHTML || 'Assign Package';
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';
    }

    // Get payment information from either modal
    const paymentMethod = document.getElementById('assignmentPaymentMethod')?.value || 
                         document.getElementById('asPaymentMethod')?.value || 'cash';
    const paymentStatus = document.getElementById('assignmentPaymentStatus')?.value || 
                         document.getElementById('asPaymentStatus')?.value || 'paid';
    const amountPaid = document.getElementById('assignmentAmountPaid')?.value ||
                      document.getElementById('asAmountPaid')?.value;
    const transactionRef = document.getElementById('assignmentTransactionRef')?.value || '';
    const discount = parseFloat(document.getElementById('assignmentDiscount')?.value || 0);

    // Calculate final amounts
    const finalAmount = Math.max(0, pricePaid - discount);
    const actualAmountPaid = paymentStatus === 'partial' ? parseFloat(amountPaid || 0) : 
                             paymentStatus === 'paid' ? finalAmount : 0;

    const data = {
        customer_id: parseInt(customerId),
        package_id: parseInt(templateId),
        package_type: packageType,
        price_paid: pricePaid,
        discount: discount,
        notes: notes,
        payment_method: paymentMethod,
        payment_status: paymentStatus,
        amount_paid: actualAmountPaid,
        balance_due: finalAmount - actualAmountPaid,
        transaction_ref: transactionRef
    };

    console.log('Sending simple assignment:', data);

    fetch('/packages/api/assign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Simple assignment response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('Simple assignment result:', result);
        if (result.success) {
            // Enhanced success message with receipt details
            const packageName = document.getElementById('asTemplateName')?.value || 'Package';
            const customerSelect = document.getElementById('asCustomer');
            const customerName = customerSelect?.options[customerSelect.selectedIndex]?.text || 'Customer';
            const paymentMethod = document.getElementById('asPaymentMethod')?.value || 'cash';
            const totalAmount = parseFloat(document.getElementById('asPricePaid')?.value) || 0;
            const discount = parseFloat(document.getElementById('asDiscount')?.value) || 0;
            const finalAmount = totalAmount - discount;
            
            // Show detailed success message
            const successMessage = `
                <div class="text-center">
                    <i class="fas fa-check-circle text-success fa-3x mb-3"></i>
                    <h5>Package Assigned Successfully!</h5>
                    <hr>
                    <p><strong>Customer:</strong> ${customerName}</p>
                    <p><strong>Package:</strong> ${packageName}</p>
                    <p><strong>Amount:</strong> ₹${finalAmount.toFixed(2)}</p>
                    <p><strong>Payment:</strong> ${paymentMethod.toUpperCase()}</p>
                    ${result.receipt_number ? `<p><strong>Receipt:</strong> ${result.receipt_number}</p>` : ''}
                </div>
            `;
            
            // Show in a modal for better visibility
            const successModal = `
                <div class="modal fade" id="successModal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-body">
                                ${successMessage}
                            </div>
                            <div class="modal-footer">
                                ${result.receipt_url ? `<a href="${result.receipt_url}" class="btn btn-outline-primary" target="_blank"><i class="fas fa-receipt me-2"></i>View Receipt</a>` : ''}
                                <button type="button" class="btn btn-success" onclick="location.reload()">OK</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.insertAdjacentHTML('beforeend', successModal);
            const modal = new bootstrap.Modal(document.getElementById('successModal'));
            modal.show();

            // Try to close any open assignment modal
            const modals = [
                'assignSimpleModal',
                'assignPackageModal', 
                'packageAssignmentModal'
            ];
            
            for (const modalId of modals) {
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                if (modal) {
                    modal.hide();
                    break;
                }
            }

            // Reset forms
            const forms = [
                'assignSimpleForm',
                'assignPackageForm',
                'packageAssignmentForm'
            ];
            
            for (const formId of forms) {
                const form = document.getElementById(formId);
                if (form) {
                    form.reset();
                }
            }

            setTimeout(() => location.reload(), 1000); // Reload page to reflect changes
        } else {
            showToast(result.error || result.message || 'Error assigning package', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving assignment:', error);
        showToast('Error assigning package: ' + error.message, 'error');
    })
    .finally(() => {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    });
}

/**
 * Generic assign package function
 */
function assignPackage(packageId, packageType) {
    console.log('Assigning package:', packageId, packageType);
    openAssignSimple(packageId, packageType);
}

/**
 * Assign Service Package function
 */
function assignServicePackage(packageId, packageName, serviceId = null) {
    console.log('Assigning service package:', packageId, packageName, serviceId);

    // Set up assignment modal for service package
    const modal = document.getElementById('assignServicePackageModal') || document.getElementById('assignPackageModal');

    if (!modal) {
        console.error('Assignment modal not found');
        showToast('Assignment modal not available', 'error');
        return;
    }

    // Reset form
    const form = document.getElementById('assignServicePackageForm') || document.getElementById('assignPackageForm');
    if (form) {
        form.reset();
    }

    // Set package details
    const packageIdInput = document.getElementById('assign_service_package_id') || document.getElementById('assign_package_id');
    const packageNameSpan = document.getElementById('assign_service_package_name') || document.getElementById('assign_package_name');

    if (packageIdInput) packageIdInput.value = packageId;
    if (packageNameSpan) packageNameSpan.textContent = packageName;

    // Set service if provided
    if (serviceId) {
        const serviceIdInput = document.getElementById('assign_service_id');
        if (serviceIdInput) serviceIdInput.value = serviceId;
    }

    // Load customers for assignment
    loadCustomersForServiceAssignment();

    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

/**
 * Clear all filters
 */
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

    currentFilters = {};
    currentPage = 1;
    loadPackages();
}

/**
 * Apply current filters
 */
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

/**
 * Open package details modal
 */
function openDetails(packageId) {
    console.log('Opening package details for:', packageId);
    openPackageDetailsModal(packageId); // Calls the correctly scoped function
}

/**
 * Open usage recording modal
 */
function openUseModal(packageId) {
    console.log('Opening usage modal for package:', packageId);

    if (packageId) {
        currentPackageId = packageId;
        openPackageDetailsModal(packageId).then(() => { // Calls the correctly scoped function
            setTimeout(() => showUsageModal(), 200);
        });
    } else if (currentPackageDetails) {
        showUsageModal();
    } else {
        showToast('Please select a package first', 'warning');
    }
}

/**
 * Open adjustment/refund modal
 */
function openAdjustModal(packageId) {
    console.log('Opening adjust modal for package:', packageId);

    if (packageId) {
        currentPackageId = packageId;
        openPackageDetailsModal(packageId).then(() => { // Calls the correctly scoped function
            setTimeout(() => showAdjustModal(), 200);
        });
    } else if (currentPackageDetails) {
        showAdjustModal();
    } else {
        showToast('Please select a package first', 'warning');
    }
}

/**
 * Change pagination page
 */
function changePage(page) {
    currentPage = page;
    loadPackages();
}

/**
 * Initialize the packages system
 */
async function initializePackages() {
    try {
        const now = new Date();
        const dateTimeInput = document.getElementById('usageDateTime');
        if (dateTimeInput) {
            dateTimeInput.value = now.toISOString().slice(0, 16);
        }

        await Promise.all([
            loadPackages(),
            loadTemplates(),
            loadCustomers(),
            loadServices(),
            loadStaff()
        ]);

        setupEventListeners(); // Setup listeners for UI elements
        console.log('Customer Packages initialized successfully');
    } catch (error) {
        console.error('Error initializing packages:', error);
        showToast('Error loading packages system', 'error');
    }
}

/**
 * Update payment summary card in real-time
 */
function updatePaymentSummary() {
    const priceInput = document.getElementById('asPricePaid');
    const discountInput = document.getElementById('asDiscount');
    const paymentStatus = document.getElementById('asPaymentStatus')?.value;
    const amountPaidInput = document.getElementById('asAmountPaid');
    
    if (!priceInput) return;
    
    const price = parseFloat(priceInput.value) || 0;
    const discount = parseFloat(discountInput?.value) || 0;
    const totalPayable = Math.max(0, price - discount);
    
    // Update summary display
    const summaryPrice = document.getElementById('summaryPrice');
    const summaryDiscount = document.getElementById('summaryDiscount');
    const summaryTotal = document.getElementById('summaryTotal');
    
    if (summaryPrice) summaryPrice.textContent = `₹${price.toFixed(2)}`;
    if (summaryDiscount) summaryDiscount.textContent = `- ₹${discount.toFixed(2)}`;
    if (summaryTotal) summaryTotal.textContent = `₹${totalPayable.toFixed(2)}`;
    
    // Auto-fill amount paid for full payment
    if (paymentStatus === 'paid' && amountPaidInput) {
        amountPaidInput.value = totalPayable.toFixed(2);
    }
    
    // Validate assign button
    validateAssignButton();
}

/**
 * Initialize service selection listener for validation
 */
document.addEventListener('DOMContentLoaded', function() {
    const serviceSelects = document.querySelectorAll('#service_assign_service_id, #assign_service_id');
    serviceSelects.forEach(select => {
        if (select) {
            select.addEventListener('change', validateAssignButton);
        }
    });
});

/**
 * Handle payment status change
 */
function handlePaymentStatusChange() {
    const paymentStatus = document.getElementById('asPaymentStatus')?.value;
    const amountPaidSection = document.getElementById('asAmountPaidSection');
    const amountPaidInput = document.getElementById('asAmountPaid');
    
    if (paymentStatus === 'partial') {
        if (amountPaidSection) amountPaidSection.style.display = 'block';
        if (amountPaidInput) amountPaidInput.required = true;
    } else {
        if (amountPaidSection) amountPaidSection.style.display = 'none';
        if (amountPaidInput) {
            amountPaidInput.required = false;
            amountPaidInput.value = '';
        }
    }
    
    updatePaymentSummary();
}

/**
 * Validate assign button state
 */
function validateAssignButton() {
    const customer = document.getElementById('asCustomer')?.value;
    const price = parseFloat(document.getElementById('asPricePaid')?.value) || 0;
    const paymentMethod = document.getElementById('asPaymentMethod')?.value;
    const paymentStatus = document.getElementById('asPaymentStatus')?.value;
    const amountPaid = parseFloat(document.getElementById('asAmountPaid')?.value) || 0;
    const packageType = document.getElementById('asPackageType')?.value || '';
    const selectedService = document.getElementById('service_assign_service_id')?.value || 
                           document.getElementById('assign_service_id')?.value;
    
    const saveBtn = document.getElementById('confirmAssignBtn') || document.getElementById('asSave');
    
    if (!saveBtn) return;
    
    // For service packages, validate service selection instead of price
    let isValid = false;
    if (packageType === 'service_package') {
        isValid = customer && selectedService && paymentMethod && paymentStatus;
    } else {
        isValid = customer && price > 0 && paymentMethod && paymentStatus;
    }
    
    // Validate partial payment amount
    if (paymentStatus === 'partial') {
        isValid = isValid && amountPaid > 0;
    }
    
    saveBtn.disabled = !isValid;
    
    // Update button text based on status
    if (isValid) {
        saveBtn.innerHTML = '<i class="fas fa-check me-2"></i>Assign Package & Collect Payment';
    } else {
        if (packageType === 'service_package' && !selectedService) {
            saveBtn.innerHTML = '<i class="fas fa-spa me-2"></i>Select Service First';
        } else {
            saveBtn.innerHTML = '<i class="fas fa-check me-2"></i>Complete All Fields';
        }
    }
}

/**
 * Setup event listeners for UI elements
 */
function setupEventListeners() {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => {
            currentFilters.q = searchInput.value;
            loadPackages();
        }, 500));
    }

    const assignForm = document.getElementById('assignPackageForm');
    if (assignForm) {
        assignForm.addEventListener('input', validateAssignForm);
    }

    const assignPackage = document.getElementById('assignPackage');
    if (assignPackage) {
        assignPackage.addEventListener('change', showPackagePreview);
    }

    // Payment status change handler for main modal
    const paymentStatusSelect = document.getElementById('assignmentPaymentStatus');
    if (paymentStatusSelect) {
        paymentStatusSelect.addEventListener('change', handlePaymentStatusChange);
    }

    // Payment method change handler for main modal
    const paymentMethodSelect = document.getElementById('assignmentPaymentMethod');
    if (paymentMethodSelect) {
        paymentMethodSelect.addEventListener('change', handlePaymentStatusChange);
    }

    // Payment status change handler for simple modal
    const asPaymentStatusSelect = document.getElementById('asPaymentStatus');
    if (asPaymentStatusSelect) {
        asPaymentStatusSelect.addEventListener('change', function() {
            const asAmountPaidSection = document.getElementById('asAmountPaidSection');
            if (this.value === 'partial') {
                if (asAmountPaidSection) asAmountPaidSection.style.display = 'block';
            } else {
                if (asAmountPaidSection) asAmountPaidSection.style.display = 'none';
            }
        });
    }

    // Price and discount change handlers
    const priceInput = document.getElementById('assignmentPrice') || document.getElementById('assignPrice');
    const discountInput = document.getElementById('assignmentDiscount');
    
    if (priceInput) {
        priceInput.addEventListener('input', calculateFinalAmount);
    }
    if (discountInput) {
        discountInput.addEventListener('input', calculateFinalAmount);
    }

    const usageForm = document.getElementById('recordUsageForm');
    if (usageForm) {
        usageForm.addEventListener('input', validateUsageForm);
    }

    const adjustForm = document.getElementById('adjustRefundForm');
    if (adjustForm) {
        adjustForm.addEventListener('input', validateAdjustForm);
    }

    // Set up multiple assign button event listeners  
    const assignButtonSelectors = [
        '#saveAssignPackage',
        '#confirmAssignBtn', 
        '#confirmAssignButton',
        '#asSave',
        '#savePackageAssignment'
    ];

    console.log('*** SETTING UP ASSIGN BUTTON EVENT LISTENERS ***');
    assignButtonSelectors.forEach(selector => {
        const btn = document.querySelector(selector);
        if (btn) {
            console.log('Found button:', selector, 'disabled:', btn.disabled, 'onclick:', btn.onclick);
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('*** BUTTON EVENT LISTENER TRIGGERED ***', selector);
                saveAssignSimple();
            });
        } else {
            console.log('Button not found:', selector);
        }
    });

    const saveUsageBtn = document.getElementById('saveUsage');
    if (saveUsageBtn) {
        saveUsageBtn.addEventListener('click', saveUsage);
    }

    const saveAdjustBtn = document.getElementById('saveAdjustment');
    if (saveAdjustBtn) {
        saveAdjustBtn.addEventListener('click', saveAdjustment);
    }

    // Set up comprehensive delegation for assign buttons
    document.addEventListener('click', function(e) {
        // Check if clicked element is an assign button
        if (e.target.matches('.btn[onclick*="Assign"]') || 
            e.target.matches('button[data-action="assign"]') ||
            e.target.closest('.btn[onclick*="Assign"]') ||
            e.target.textContent?.includes('Assign') && e.target.classList.contains('btn')) {
            
            // Only handle if it's in an assignment modal
            const assignModal = e.target.closest('#assignPackageModal, #assignSimpleModal, #packageAssignmentModal');
            if (assignModal) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Assign button clicked via delegation');
                saveAssignSimple();
            }
        }
    });

    // Specific handler for the blue "Assign" button in the modal
    setTimeout(() => {
        const assignBtns = document.querySelectorAll('.btn-primary');
        assignBtns.forEach(btn => {
            if (btn.textContent.includes('Assign') && !btn.hasAttribute('data-assign-listener')) {
                btn.setAttribute('data-assign-listener', 'true');
                btn.addEventListener('click', function(e) {
                    const modal = this.closest('.modal');
                    if (modal && (modal.id.includes('assign') || modal.id.includes('package'))) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.log('Blue assign button clicked');
                        saveAssignSimple();
                    }
                });
            }
        });
    }, 1000);
}

/**
 * Load packages with current filters applied
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
 * Load package templates from API
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
 * Load customers from API
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
 * Load customers for assignment modal dropdown
 */
async function loadCustomersForAssignment() {
    try {
        const response = await fetch('/packages/api/customers');
        const result = await response.json();

        // Try multiple possible customer select elements
        const customerSelect = document.getElementById('assignCustomerSelect') || 
                             document.getElementById('asCustomer') ||
                             document.querySelector('select[name="customer_id"]');

        if (!customerSelect) {
            console.error('Customer select element not found');
            return;
        }

        customerSelect.innerHTML = '<option value="">Select customer...</option>';

        if (result.success && result.customers) {
            result.customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = `${customer.name} - ${customer.phone || 'No phone'}`;
                customerSelect.appendChild(option);
            });
        }

        // Enable save button when customer is selected
        customerSelect.addEventListener('change', function() {
            const saveBtn = document.getElementById('confirmAssignBtn') || 
                           document.getElementById('asSave') ||
                           document.querySelector('.btn-primary[onclick*="assign"]');
            if (saveBtn) {
                saveBtn.disabled = !this.value;
            }
        });

    } catch (error) {
        console.error('Error loading customers:', error);
        showToast('Error loading customers', 'error');
    }
}

/**
 * Load customers for simple assign modal dropdown (legacy support)
 */
async function loadCustomersForSimpleAssign() {
    return loadCustomersForAssignment();
}

/**
 * Load customers for service package assignment
 */
async function loadCustomersForServiceAssignment() {
    try {
        const response = await fetch('/packages/api/customers');
        const result = await response.json();

        const customerSelect = document.getElementById('assign_service_customer') || 
                             document.getElementById('assignCustomer') ||
                             document.querySelector('select[name="customer_id"]');

        if (!customerSelect) {
            console.error('Customer select element not found');
            return;
        }

        customerSelect.innerHTML = '<option value="">Select customer...</option>';

        if (result.success && result.customers) {
            result.customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = `${customer.name} - ${customer.phone || 'No phone'}`;
                customerSelect.appendChild(option);
            });
        }

        // Enable save button when customer is selected
        customerSelect.addEventListener('change', function() {
            const saveBtn = document.getElementById('confirmServiceAssignBtn') || 
                           document.getElementById('saveServiceAssignment');
            if (saveBtn) {
                saveBtn.disabled = !this.value;
            }
        });

    } catch (error) {
        console.error('Error loading customers:', error);
        showToast('Error loading customers', 'error');
    }
}

/**
 * Load services from API
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
 * Load staff from API
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
 * Populate dropdowns with loaded data
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
 * Render the packages table with loaded data
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
                <td><strong>${pkg.customer_name}</strong></td>
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
 * Get CSS class for status badge based on status
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
 * Update pagination controls based on API response
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
 * Show package preview when a template is selected in the dropdown
 */
function showPackagePreview() {
    const select = document.getElementById('assignPackage');
    const preview = document.getElementById('packagePreview');
    const itemsContainer = document.getElementById('packageItems');
    const priceInput = document.getElementById('assignPrice');

    if (select.value) {
        const selectedOption = select.selectedOptions[0];
        const template = JSON.parse(selectedOption.dataset.template);

        priceInput.value = template.price;

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

    validateAssignForm(); // Re-validate form when preview changes
}

/**
 * Validate the assignment form fields - PAYMENT MUST BE CONFIRMED
 */
function validateAssignForm() {
    const form = document.getElementById('assignPackageForm');
    const saveBtn = document.getElementById('saveAssignPackage');

    const customer = document.getElementById('assignCustomer')?.value;
    const package = document.getElementById('assignPackage')?.value;
    const price = document.getElementById('assignPrice')?.value;
    const paymentMethod = document.getElementById('assignmentPaymentMethod')?.value;
    const paymentStatus = document.getElementById('assignmentPaymentStatus')?.value;

    // Basic validation: customer, package, price must be filled
    let isValid = customer && package && price && parseFloat(price) > 0;
    
    // PAYMENT VALIDATION - Required before assignment
    if (!paymentMethod) {
        isValid = false;
    }
    
    if (!paymentStatus) {
        isValid = false;
    }
    
    // Only allow assignment if payment is confirmed (paid or partial)
    if (paymentStatus && paymentStatus !== 'paid' && paymentStatus !== 'partial') {
        isValid = false;
        if (saveBtn) {
            saveBtn.title = 'Payment must be completed before assignment';
        }
    }
    
    // For partial payments, validate amount paid
    if (paymentStatus === 'partial') {
        const amountPaid = document.getElementById('assignmentAmountPaid')?.value;
        if (!amountPaid || parseFloat(amountPaid) <= 0) {
            isValid = false;
        }
    }

    if (saveBtn) {
        saveBtn.disabled = !isValid;
        if (isValid) {
            saveBtn.title = 'Assign package after payment confirmation';
        }
    }

    if (form) {
        form.classList.toggle('was-validated', isValid);
    }
}

/**
 * Handle payment status changes and show/hide amount paid field
 */
function handlePaymentStatusChange() {
    const paymentStatus = document.getElementById('assignmentPaymentStatus')?.value;
    const amountPaidSection = document.getElementById('amountPaidSection');
    const amountPaidInput = document.getElementById('assignmentAmountPaid');
    const transactionRefSection = document.getElementById('transactionRefSection');
    const paymentMethod = document.getElementById('assignmentPaymentMethod')?.value;

    if (paymentStatus === 'partial') {
        // Show amount paid field for partial payments
        if (amountPaidSection) amountPaidSection.style.display = 'block';
        if (amountPaidInput) amountPaidInput.required = true;
    } else {
        // Hide for full/pending payments
        if (amountPaidSection) amountPaidSection.style.display = 'none';
        if (amountPaidInput) {
            amountPaidInput.required = false;
            amountPaidInput.value = '';
        }
    }

    // Show transaction reference for non-cash payments
    if (transactionRefSection) {
        transactionRefSection.style.display = (paymentMethod && paymentMethod !== 'cash') ? 'block' : 'none';
    }

    validateAssignForm();
}

/**
 * Calculate final amount after discount
 */
function calculateFinalAmount() {
    const priceInput = document.getElementById('assignmentPrice') || document.getElementById('assignPrice') || document.getElementById('asPricePaid');
    const discountInput = document.getElementById('assignmentDiscount') || document.getElementById('assignDiscount');
    
    if (!priceInput) return;
    
    const price = parseFloat(priceInput.value) || 0;
    const discount = parseFloat(discountInput?.value) || 0;
    const finalAmount = Math.max(0, price - discount);
    
    // Update amount paid for full payment status
    const paymentStatus = document.getElementById('assignmentPaymentStatus')?.value;
    const amountPaidInput = document.getElementById('assignmentAmountPaid');
    
    if (paymentStatus === 'paid' && amountPaidInput) {
        amountPaidInput.value = finalAmount.toFixed(2);
    }
    
    // Update payment summary display
    updatePaymentSummary(price, discount, finalAmount, paymentStatus, amountPaidInput?.value);
    
    return finalAmount;
}

/**
 * Update payment summary card with real-time calculations
 */
function updatePaymentSummary(price, discount, finalAmount, paymentStatus, amountPaid) {
    const summaryPrice = document.getElementById('summaryPrice');
    const summaryDiscount = document.getElementById('summaryDiscount');
    const summaryFinal = document.getElementById('summaryFinal');
    const summaryBalance = document.getElementById('summaryBalance');
    const summaryBalanceSection = document.getElementById('summaryBalanceSection');
    
    if (summaryPrice) summaryPrice.textContent = price.toFixed(2);
    if (summaryDiscount) summaryDiscount.textContent = discount.toFixed(2);
    if (summaryFinal) summaryFinal.textContent = finalAmount.toFixed(2);
    
    // Show balance for partial payments
    if (paymentStatus === 'partial' && amountPaid) {
        const balance = finalAmount - parseFloat(amountPaid || 0);
        if (summaryBalance) summaryBalance.textContent = Math.max(0, balance).toFixed(2);
        if (summaryBalanceSection) summaryBalanceSection.style.display = 'block';
    } else {
        if (summaryBalanceSection) summaryBalanceSection.style.display = 'none';
    }
}

/**
 * Save the package assignment to the backend
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
            formData.expires_on = expiresInput.value + 'T23:59:59'; // Set to end of day
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
            bootstrap.Modal.getInstance(document.getElementById('assignPackageModal')).hide(); // Close the modal
            setTimeout(() => location.reload(), 1000); // Reload page to show updated assignments
        } else {
            showToast('Error: ' + (data.message || data.error), 'error');
        }
    } catch (error) {
        console.error('Error saving assignment:', error);
        showToast('Error assigning package', 'error');
    }
}

/**
 * Save service package assignment
 */
async function saveServicePackageAssignment() {
    console.log('Saving service package assignment...');

    const packageId = document.getElementById('assign_service_package_id')?.value || 
                     document.getElementById('assign_package_id')?.value;
    const customerId = document.getElementById('assign_service_customer')?.value || 
                      document.getElementById('assignCustomer')?.value;
    const serviceId = document.getElementById('assign_service_id')?.value;
    const notes = document.getElementById('assign_service_notes')?.value || '';

    if (!packageId || !customerId) {
        showToast('Please select a customer and package', 'warning');
        return;
    }

    const saveBtn = document.getElementById('confirmServiceAssignBtn') || 
                   document.getElementById('saveServiceAssignment');
    const originalText = saveBtn?.innerHTML;

    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';
    }

    const data = {
        customer_id: parseInt(customerId),
        package_id: parseInt(packageId),
        package_type: 'service_package',
        service_id: serviceId ? parseInt(serviceId) : null,
        notes: notes
    };

    try {
        const response = await fetch('/packages/api/assign-service-package', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('Service package assigned successfully!', 'success');

            const modal = bootstrap.Modal.getInstance(
                document.getElementById('assignServicePackageModal') || 
                document.getElementById('assignPackageModal')
            );
            if (modal) {
                modal.hide();
            }

            // Reset form
            const form = document.getElementById('assignServicePackageForm') || 
                        document.getElementById('assignPackageForm');
            if (form) {
                form.reset();
            }

            // Reload page to reflect changes
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(result.error || 'Error assigning service package', 'error');
        }
    } catch (error) {
        console.error('Error saving service package assignment:', error);
        showToast('Error assigning service package', 'error');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    }
}

// Make saveServicePackageAssignment globally available
window.saveServicePackageAssignment = saveServicePackageAssignment;

/**
 * Open package details modal and populate it
 */
async function openPackageDetailsModal(packageId) {
    try {
        currentPackageId = packageId; // Store the ID for potential later use

        const response = await fetch(`/packages/api/customer-packages/${packageId}`);
        const data = await response.json();

        if (data.success) {
            currentPackageDetails = data.package; // Store details for other functions
            renderPackageDetails(); // Populate the modal

            const modal = new bootstrap.Modal(document.getElementById('packageDetailsModal'));
            modal.show();

            return Promise.resolve(); // Return a promise for chaining
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
 * Show the usage recording modal
 */
function showUsageModal() {
    if (!currentPackageDetails) {
        showToast('Package details not loaded', 'error');
        return;
    }

    // Reset the form
    const form = document.getElementById('recordUsageForm');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }

    // Set current date/time for usage
    const now = new Date();
    const dateTimeInput = document.getElementById('usageDateTime');
    if (dateTimeInput) {
        dateTimeInput.value = now.toISOString().slice(0, 16);
    }

    // Populate services dropdown based on remaining items in the package
    const serviceSelect = document.getElementById('usageService');
    if (serviceSelect) {
        serviceSelect.innerHTML = '<option value="">Select service...</option>';

        if (currentPackageDetails.items) {
            currentPackageDetails.items.forEach(item => {
                if (item.remaining_qty > 0) {
                    const option = document.createElement('option');
                    option.value = item.service_id;
                    option.textContent = `${item.service_name} (${item.remaining_qty} remaining)`;
                    option.dataset.remaining = item.remaining_qty; // Store remaining quantity for validation
                    serviceSelect.appendChild(option);
                }
            });
        }
    }

    // Hide any previous hints
    const hint = document.getElementById('usageHint');
    if (hint) {
        hint.style.display = 'none';
    }

    const modal = new bootstrap.Modal(document.getElementById('recordUsageModal'));
    modal.show();
}

/**
 * Show the adjustment/refund modal
 */
function showAdjustModal() {
    if (!currentPackageDetails) {
        showToast('Package details not loaded', 'error');
        return;
    }

    // Reset the form
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

    // Populate services dropdown based on package items
    const serviceSelect = document.getElementById('adjustService');
    if (serviceSelect) {
        serviceSelect.innerHTML = '<option value="">Select service...</option>';

        if (currentPackageDetails.items) {
            currentPackageDetails.items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.service_id;
                option.textContent = `${item.service_name} (${item.used_qty} used, ${item.remaining_qty} remaining)`;
                option.dataset.used = item.used_qty; // Store used quantity for validation
                option.dataset.remaining = item.remaining_qty; // Store remaining quantity
                option.dataset.total = item.total_qty; // Store total quantity
                serviceSelect.appendChild(option);
            });
        }
    }

    // Hide any previous hints
    const hint = document.getElementById('adjustHint');
    if (hint) {
        hint.style.display = 'none';
    }

    const modal = new bootstrap.Modal(document.getElementById('adjustRefundModal'));
    modal.show();
}

/**
 * Render the package details in the modal body
 */
function renderPackageDetails() {
    if (!currentPackageDetails) return;

    const pkg = currentPackageDetails;

    // Populate header information
    document.getElementById('detailCustomerName').textContent = pkg.customer_name;
    document.getElementById('detailPackageName').textContent = pkg.package_name;
    document.getElementById('detailPrice').textContent = pkg.price_paid ? pkg.price_paid.toFixed(2) : '0.00';
    document.getElementById('detailAssigned').textContent = pkg.assigned_on || 'N/A';
    document.getElementById('detailExpires').textContent = pkg.expires_on || 'No expiry';

    const statusBadge = document.getElementById('detailStatus');
    statusBadge.textContent = pkg.status || 'Unknown';
    statusBadge.className = `badge ${getStatusClass(pkg.status || 'active')}`; // Use helper function for badge class

    // Populate service items section with complete details
    const serviceItems = document.getElementById('serviceItems');
    if (pkg.items && pkg.items.length > 0) {
        serviceItems.innerHTML = pkg.items.map(item => {
            // Calculate progress percentage for the service item
            const totalQty = item.total_qty || 0;
            const usedQty = item.used_qty || 0;
            const remainingQty = totalQty - usedQty;
            const progressPercent = totalQty > 0 ? ((usedQty / totalQty) * 100).toFixed(1) : 0;
            
            return `
                <div class="col-12 mb-3">
                    <div class="card border-${progressPercent >= 100 ? 'danger' : progressPercent >= 75 ? 'warning' : 'success'}">
                        <div class="card-body">
                            <h6 class="mb-2">
                                <i class="fas fa-spa me-2"></i>${item.service_name || 'Unknown Service'}
                            </h6>
                            <div class="row">
                                <div class="col-md-4">
                                    <small class="text-muted">Total Sessions:</small>
                                    <div class="fw-bold">${totalQty}</div>
                                </div>
                                <div class="col-md-4">
                                    <small class="text-muted">Used:</small>
                                    <div class="fw-bold text-primary">${usedQty}</div>
                                </div>
                                <div class="col-md-4">
                                    <small class="text-muted">Remaining:</small>
                                    <div class="fw-bold text-success">${remainingQty}</div>
                                </div>
                            </div>
                            <div class="progress mt-2" style="height: 20px;">
                                <div class="progress-bar ${progressPercent >= 100 ? 'bg-danger' : progressPercent >= 75 ? 'bg-warning' : 'bg-success'}" 
                                     role="progressbar" 
                                     style="width: ${Math.min(progressPercent, 100)}%"
                                     aria-valuenow="${progressPercent}" 
                                     aria-valuemin="0" 
                                     aria-valuemax="100">
                                    ${progressPercent}% Used
                                </div>
                            </div>
                            ${item.discount > 0 ? `
                                <div class="mt-2">
                                    <span class="badge bg-success">
                                        <i class="fas fa-tag me-1"></i>${item.discount}% Discount Applied
                                    </span>
                                </div>
                            ` : ''}
                            ${item.original_price ? `
                                <div class="mt-2">
                                    <small class="text-muted">Price per session: ₹${item.original_price.toFixed(2)}</small>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        serviceItems.innerHTML = `
            <div class="col-12">
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>No service details available for this package.
                </div>
            </div>
        `;
    }

    // Populate usage history section with complete details
    const usageHistory = document.getElementById('usageHistory');
    if (pkg.usage_history && pkg.usage_history.length > 0) {
        usageHistory.innerHTML = pkg.usage_history.slice(0, 10).map(usage => {
            return `
                <tr>
                    <td>${usage.used_on || 'N/A'}</td>
                    <td>${usage.service_name || 'N/A'}</td>
                    <td>
                        <span class="badge bg-primary">${usage.qty_used || 0} session(s)</span>
                    </td>
                    <td>
                        ${usage.invoice_id ? `
                            <a href="/integrated-billing/invoice/${usage.invoice_id}" 
                               class="btn btn-sm btn-outline-primary" 
                               target="_blank">
                                <i class="fas fa-receipt me-1"></i>INV-${usage.invoice_id}
                            </a>
                        ` : '<span class="text-muted">N/A</span>'}
                    </td>
                    <td>
                        <small class="text-muted">${usage.notes || 'No notes'}</small>
                    </td>
                </tr>
            `;
        }).join('');
    } else {
        usageHistory.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted">
                    <i class="fas fa-inbox me-2"></i>No usage history yet
                </td>
            </tr>
        `;
    }

    // Add package type indicator
    const packageTypeInfo = document.getElementById('packageTypeInfo');
    if (packageTypeInfo) {
        let typeIcon = 'fa-gift';
        let typeText = 'Standard Package';
        let typeColor = 'primary';
        
        if (pkg.package_type === 'membership') {
            typeIcon = 'fa-crown';
            typeText = 'Membership Package';
            typeColor = 'warning';
        } else if (pkg.package_type === 'service_package') {
            typeIcon = 'fa-box';
            typeText = 'Service Package';
            typeColor = 'info';
        } else if (pkg.package_type === 'prepaid') {
            typeIcon = 'fa-wallet';
            typeText = 'Prepaid Package';
            typeColor = 'success';
        }
        
        packageTypeInfo.innerHTML = `
            <span class="badge bg-${typeColor}">
                <i class="fas ${typeIcon} me-1"></i>${typeText}
            </span>
        `;
    }

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

    // Populate recent usage table
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
 * Validate the usage form before submission
 */
function validateUsageForm() {
    const form = document.getElementById('recordUsageForm');
    const saveBtn = document.getElementById('saveUsage');

    const service = document.getElementById('usageService').value;
    const quantity = document.getElementById('usageQuantity').value;

    let isValid = service && quantity && parseInt(quantity) > 0;

    // Additional check: ensure enough remaining balance
    if (isValid && service) {
        const selectedOption = document.getElementById('usageService').selectedOptions[0];
        const remaining = parseInt(selectedOption.dataset.remaining);
        isValid = parseInt(quantity) <= remaining;
    }

    if (saveBtn) {
        saveBtn.disabled = !isValid;
    }
    if (form) {
        form.classList.toggle('was-validated', isValid);
    }
}

/**
 * Save the recorded usage to the backend
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

            const modal = bootstrap.Modal.getInstance(document.getElementById('recordUsageModal'));
            modal.hide();

            // Refresh package details and the main package list
            await Promise.all([
                openDetails(currentPackageId), // Re-opens details to show updated usage
                loadPackages() // Reloads the main package list
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
 * Validate the adjustment/refund form
 */
function validateAdjustForm() {
    const form = document.getElementById('adjustRefundForm');
    const saveBtn = document.getElementById('saveAdjustment');

    const service = document.getElementById('adjustService').value;
    const quantity = document.getElementById('adjustQuantity').value;
    const reason = document.getElementById('adjustReason').value;
    const mode = document.querySelector('input[name="adjustMode"]:checked').value;

    let isValid = service && quantity && parseInt(quantity) > 0 && reason.trim();

    // Specific validation based on mode (refund/adjust)
    if (isValid && service) {
        const selectedOption = document.getElementById('adjustService').selectedOptions[0];
        const used = parseInt(selectedOption.dataset.used);
        const total = parseInt(selectedOption.dataset.total);
        const qty = parseInt(quantity);

        if (mode === 'refund') {
            isValid = qty <= used; // Cannot refund more than used
        } else { // 'adjust' mode
            const newTotal = total + qty;
            const newRemaining = newTotal - used;
            isValid = newRemaining >= 0; // Cannot result in negative remaining balance
        }
    }

    if (saveBtn) {
        saveBtn.disabled = !isValid;
    }
    if (form) {
        form.classList.toggle('was-validated', isValid);
    }
}

/**
 * Save the adjustment or refund operation
 */
async function saveAdjustment() {
    try {
        const mode = document.querySelector('input[name="adjustMode"]:checked').value;

        const formData = {
            service_id: parseInt(document.getElementById('adjustService').value),
            qty: parseInt(document.getElementById('adjustQuantity').value),
            reason: document.getElementById('adjustReason').value,
            change_type: mode // 'refund' or 'adjust'
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

            const modal = bootstrap.Modal.getInstance(document.getElementById('adjustRefundModal'));
            modal.hide();

            // Refresh package details and the main package list
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

// ========================================
// STUDENT OFFER MANAGEMENT
// ========================================

async function loadStudentPackages() {
    try {
        console.log('Loading student packages...');

        const response = await fetch('/packages/api/student-offers');
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

                row.innerHTML = `
                    <td><strong>${offer.name || 'Student Offer'}</strong></td>
                    <td><small>${servicesList}</small></td>
                    <td><span class="badge bg-success">${offer.discount_percentage}%</span></td>
                    <td>
                        <small>
                            <strong>From:</strong> ${offer.valid_from}<br>
                            <strong>To:</strong> ${offer.valid_to}
                        </small>
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-success btn-sm"
                                    onclick="openAssignSimple(${offer.id}, 'student_offer')"
                                    title="Assign to Customer">
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

            const countElement = document.getElementById('student-total-count');
            if (countElement) {
                countElement.textContent = data.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
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

function editStudentOffer(offerId) {
    console.log('Edit student offer:', offerId);
    window.location.href = `/packages/student-offers/edit/${offerId}`;
}

function deleteStudentOffer(offerId) {
    if (!confirm('Are you sure you want to delete this student offer?')) {
        return;
    }

    fetch(`/packages/api/student-offers/${offerId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success || response.ok) {
            showToast('Student offer deleted successfully!', 'success');
            loadStudentPackages();
        } else {
            throw new Error(result.error || 'Failed to delete student offer');
        }
    })
    .catch(error => {
        console.error('Error deleting student offer:', error);
        showToast('Error deleting student offer: ' + error.message, 'error');
    });
}

function assignStudentOffer(offerId) {
    openAssignSimple(offerId, 'student_offer');
}

function saveStudentOffer() {
    console.log('Save student offer function called');
    showToast('Save functionality will be available soon', 'info');
}

function updateStudentOffer() {
    console.log('Update student offer function called');
    showToast('Update functionality will be available soon', 'info');
}

function initializeStudentOfferModals() {
    console.log('Initializing student offer modals...');
    // Further initialization logic for student offer modals would go here
}

// ========================================
// MEMBERSHIP PACKAGES
// ========================================

async function loadMembershipPackages() {
    try {
        console.log('Loading membership packages...');

        const response = await fetch('/api/memberships');
        const data = await response.json();

        const tableBody = document.querySelector('#tblMemberships tbody');
        if (!tableBody) {
            console.error('Memberships table body not found');
            return;
        }

        tableBody.innerHTML = '';

        if (data && data.length > 0) {
            data.forEach(pkg => {
                const row = document.createElement('tr');

                row.innerHTML = `
                    <td><strong>${pkg.name}</strong></td>
                    <td>₹${parseFloat(pkg.price || 0).toLocaleString()}</td>
                    <td>${pkg.validity_months || 12} months</td>
                    <td>${pkg.description || 'No description'}</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="openAssignSimple(${pkg.id}, 'membership')" title="Assign">
                            <i class="fas fa-user-plus"></i> Assign
                        </button>
                    </td>
                `;

                tableBody.appendChild(row);
            });

            const countElement = document.getElementById('membership-total-count');
            if (countElement) {
                countElement.textContent = data.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No membership packages found
                    </td>
                </tr>
            `;
        }

        console.log(`Successfully loaded ${data.length || 0} membership packages`);

    } catch (error) {
        console.error('Error loading membership packages:', error);
        showToast('Error loading membership packages', 'error');
    }
}

// ========================================
// YEARLY PACKAGES
// ========================================

async function loadYearlyPackages() {
    try {
        console.log('Loading yearly packages...');

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
                    <td>${pkg.validity_months || 12} months</td>
                    <td>${pkg.discount_percent || 0}%</td>
                    <td>
                        <button class="btn btn-primary btn-sm" onclick="openAssignSimple(${pkg.id}, 'yearly')" title="Assign">
                            <i class="fas fa-user-plus"></i> Assign
                        </button>
                    </td>
                `;

                tableBody.appendChild(row);
            });

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

// ========================================
// KITTY PARTY PACKAGES  
// ========================================

async function loadKittyPackages() {
    try {
        console.log('Loading kitty party packages...');

        const response = await fetch('/api/kitty-parties');
        const data = await response.json();

        const tableBody = document.querySelector('#tblKittyPackages tbody');
        if (!tableBody) {
            console.error('Kitty packages table body not found');
            return;
        }

        tableBody.innerHTML = '';

        if (data.success && data.parties) {
            data.parties.forEach(party => {
                const row = document.createElement('tr');
                const servicesList = party.services && party.services.length > 0 ?
                    party.services.map(s => s.name).join(', ') : 'No services selected';
                const validPeriod = party.valid_from && party.valid_to ?
                    `${party.valid_from} to ${party.valid_to}` : 'No validity period';
                const statusBadge = party.is_active ?
                    '<span class="badge bg-success">Active</span>' :
                    '<span class="badge bg-secondary">Inactive</span>';

                row.innerHTML = `
                    <td><strong>${party.name}</strong></td>
                    <td>₹${party.price}</td>
                    <td>${party.min_guests}</td>
                    <td><small>${servicesList}</small></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-warning" onclick="editKittyParty(${party.id})" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteKittyParty(${party.id})" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                            <button class="btn btn-primary" onclick="assignKittyParty(${party.id})" title="Assign">
                                <i class="fas fa-user-plus"></i> Assign
                            </button>
                        </div>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            const countElement = document.getElementById('kitty-total-count');
            if (countElement) {
                countElement.textContent = data.parties.length;
            }
        } else {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-info-circle me-2"></i>
                        No kitty parties found
                    </td>
                </tr>
            `;
        }

        console.log(`Successfully loaded ${data.parties?.length || 0} kitty parties`);

    } catch (error) {
        console.error('Error loading kitty party packages:', error);
        showToast('Error loading kitty party packages', 'error');
    }
}

function editKittyParty(partyId) {
    console.log('Edit kitty party:', partyId);
    showToast('Edit functionality will be available soon', 'info');
}

function deleteKittyParty(partyId) {
    if (!confirm('Are you sure you want to delete this kitty party?')) {
        return;
    }

    fetch(`/api/kitty-parties/${partyId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success || response.ok) {
            showToast('Kitty party deleted successfully!', 'success');
            loadKittyPackages();
        } else {
            throw new Error(result.error || 'Failed to delete kitty party');
        }
    })
    .catch(error => {
        console.error('Error deleting kitty party:', error);
        showToast('Error deleting kitty party: ' + error.message, 'error');
    });
}

function assignKittyParty(partyId) {
    openAssignSimple(partyId, 'kitty');
}

function saveKittyParty() {
    console.log('Save kitty party function called');
    showToast('Save functionality will be available soon', 'info');
}

function updateKittyParty() {
    console.log('Update kitty party function called');
    showToast('Update functionality will be available soon', 'info');
}

function initializeKittyPartyModals() {
    console.log('Initializing kitty party modals...');
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

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
}

function viewAssignmentDetails(assignmentId) {
    console.log('View assignment details:', assignmentId);
    showToast('Assignment details functionality will be available soon', 'info');
}

function viewCustomerDetails(customerId) {
    console.log('View customer details:', customerId);
    showToast('Customer details functionality will be available soon', 'info');
}

function confirmPackageAssignment() {
    console.log('Confirming package assignment...');

    // Get form data from the modal - check multiple possible element IDs
    const offerType = document.getElementById('assignOfferType')?.value || 
                     document.getElementById('asPackageType')?.value || 'membership';
    const offerReferenceId = document.getElementById('assignOfferReferenceId')?.value || 
                            document.getElementById('asTemplateId')?.value;
    const customerId = document.getElementById('assignCustomerSelect')?.value || 
                      document.getElementById('asCustomer')?.value;
    const pricePaid = parseFloat(document.getElementById('assignPricePaid')?.value || 
                                document.getElementById('asPricePaid')?.value) || 0;
    const notes = document.getElementById('assignNotes')?.value || 
                 document.getElementById('asNotes')?.value || '';

    console.log('Assignment data:', {
        offerType,
        offerReferenceId,
        customerId,
        pricePaid,
        notes
    });

    if (!customerId || !offerReferenceId) {
        showToast('Please select a customer and package', 'warning');
        return;
    }

    const data = {
        customer_id: parseInt(customerId),
        package_id: parseInt(offerReferenceId),
        package_type: offerType,
        price_paid: pricePaid,
        notes: notes
    };

    console.log('Sending assignment data:', data);

    const saveBtn = document.getElementById('confirmAssignBtn') || 
                   document.getElementById('asSave');
    const originalText = saveBtn?.innerHTML || 'Assign Package';
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';
    }

    fetch('/packages/api/assign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('Assignment result:', result);
        if (result.success) {
            showToast('Package assigned successfully!', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignPackageModal')) ||
                         bootstrap.Modal.getInstance(document.getElementById('assignSimpleModal'));
            if (modal) modal.hide();

            // Reset form
            const form = document.getElementById('assignPackageForm') || 
                        document.getElementById('assignSimpleForm');
            if (form) form.reset();

            setTimeout(() => location.reload(), 1000);
        } else {
            showToast(result.error || result.message || 'Error assigning package', 'error');
        }
    })
    .catch(error => {
        console.error('Error assigning package:', error);
        showToast('Error assigning package: ' + error.message, 'error');
    })
    .finally(() => {
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.innerHTML = originalText;
        }
    });
}

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

    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}