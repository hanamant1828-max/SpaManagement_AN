/**
 * Student Offers Management JavaScript
 * Handles add, edit, delete, and view operations for student offers
 */

// Global variables
let studentServices = [];
let currentStudentOffers = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Student Offers JS loaded');

    // Only initialize if we're on a page that needs it
    if (document.getElementById('addStudentOfferForm') || document.getElementById('editStudentOfferForm') || document.getElementById('tblStudentOffers')) {
        initializeStudentOffers();
    }
});

/**
 * Initialize student offers system
 */
async function initializeStudentOffers() {
    try {
        // Load services and set up event listeners
        await loadServicesForStudentOffers();
        setupStudentOfferEventListeners();
        setDefaultDates();

        // Load offers table if it exists
        if (document.getElementById('tblStudentOffers')) {
            await loadStudentOffersTable();
        }

        console.log('Student Offers initialized successfully');
    } catch (error) {
        console.error('Error initializing student offers:', error);
        showToast('Error loading student offers system', 'error');
    }
}

/**
 * Set default dates for forms
 */
function setDefaultDates() {
    const today = new Date().toISOString().split('T')[0];
    const sixMonthsLater = new Date();
    sixMonthsLater.setMonth(sixMonthsLater.getMonth() + 6);
    const futureDate = sixMonthsLater.toISOString().split('T')[0];

    // Set defaults for add form
    const validFromField = document.getElementById('validFrom');
    const validToField = document.getElementById('validTo');

    if (validFromField && !validFromField.value) validFromField.value = today;
    if (validToField && !validToField.value) validToField.value = futureDate;
}

/**
 * Load services for student offer dropdowns
 */
async function loadServicesForStudentOffers() {
    try {
        const response = await fetch('/packages/api/services');
        const data = await response.json();

        if (data.success && data.services) {
            studentServices = data.services;

            // Populate add form dropdown
            const addSelect = document.getElementById('serviceIds');
            if (addSelect) {
                addSelect.innerHTML = ''; // Clear existing options
                data.services.forEach(service => {
                    const option = document.createElement('option');
                    option.value = service.id;
                    option.textContent = `${service.name} - ₹${service.price}`;
                    addSelect.appendChild(option);
                });
            }

            // Populate edit form dropdown
            const editSelect = document.getElementById('editStudentOfferServices');
            if (editSelect) {
                editSelect.innerHTML = ''; // Clear existing options
                data.services.forEach(service => {
                    const option = document.createElement('option');
                    option.value = service.id;
                    option.textContent = `${service.name} - ₹${service.price}`;
                    editSelect.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Error loading services:', error);
        showToast('Error loading services', 'error');
    }
}

/**
 * Setup event listeners for student offer forms
 */
function setupStudentOfferEventListeners() {
    // Add form validation and submission
    const addForm = document.getElementById('addStudentOfferForm');
    if (addForm) {
        addForm.addEventListener('input', validateStudentOfferForm);
        addForm.addEventListener('change', validateStudentOfferForm);
        addForm.addEventListener('submit', handleFormSubmit);
    }

    // Edit form validation
    const editForm = document.getElementById('editStudentOfferForm');
    if (editForm) {
        editForm.addEventListener('input', validateEditStudentOfferForm);
        editForm.addEventListener('change', validateEditStudentOfferForm);
        editForm.addEventListener('submit', handleEditFormSubmit);
    }

    // Valid days dropdown change handler
    const validDaysSelect = document.getElementById('validDays');
    if (validDaysSelect) {
        validDaysSelect.addEventListener('change', function() {
            const customDiv = document.getElementById('customValidDaysDiv');
            if (this.value === 'Custom') {
                customDiv.style.display = 'block';
            } else {
                customDiv.style.display = 'none';
            }
            validateStudentOfferForm();
        });
    }

    // Edit valid days dropdown change handler
    const editValidDaysSelect = document.getElementById('editStudentValidDays');
    if (editValidDaysSelect) {
        editValidDaysSelect.addEventListener('change', function() {
            const editCustomDiv = document.getElementById('editCustomValidDaysDiv');
            if (this.value === 'Custom') {
                editCustomDiv.style.display = 'block';
            } else {
                editCustomDiv.style.display = 'none';
            }
            validateEditStudentOfferForm();
        });
    }

    // Save button click handler
    const saveBtn = document.getElementById('saveStudentOfferBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default form submission
            handleFormSubmit(e);
        });
    }
}

/**
 * Validate student offer form (ADD form)
 */
function validateStudentOfferForm() {
    const servicesSelect = document.getElementById('serviceIds');
    const discountInput = document.getElementById('discountPercentage');
    const validFromInput = document.getElementById('validFrom');
    const validToInput = document.getElementById('validTo');
    const saveBtn = document.getElementById('saveStudentOfferBtn');

    let errors = [];

    // Service validation
    const selectedServicesCount = servicesSelect ? servicesSelect.selectedOptions.length : 0;
    if (selectedServicesCount === 0) {
        errors.push('At least one service must be selected.');
    }

    // Discount validation
    let discountValue = discountInput ? parseFloat(discountInput.value) : NaN;
    if (isNaN(discountValue) || discountValue < 1 || discountValue > 100) {
        errors.push('Discount percentage must be between 1 and 100.');
    }

    // Date validation
    let validFromDate = validFromInput ? new Date(validFromInput.value) : null;
    let validToDate = validToInput ? new Date(validToInput.value) : null;

    if (!validFromDate || isNaN(validFromDate.getTime())) {
        errors.push('Valid From date is required.');
    }
    if (!validToDate || isNaN(validToDate.getTime())) {
        errors.push('Valid Until date is required.');
    }
    if (validFromDate && validToDate && validToDate < validFromDate) {
        errors.push('Valid Until date must be on or after Valid From date.');
    }

    // Display errors
    const errorDiv = document.getElementById('addStudentOfferFormError');
    if (errorDiv) {
        if (errors.length > 0) {
            errorDiv.innerHTML = errors.join('<br>');
            errorDiv.style.display = 'block';
        } else {
            errorDiv.style.display = 'none';
        }
    }

    // Enable/disable save button
    if (saveBtn) {
        saveBtn.disabled = errors.length > 0;
    }

    // Update preview
    updateStudentOfferPreview();
}

/**
 * Validate edit student offer form (EDIT form)
 */
function validateEditStudentOfferForm() {
    // Use checkboxes for edit form (services container)
    const servicesCheckboxes = document.querySelectorAll('input[name="service_ids"]:checked');
    const discountInput = document.getElementById('discountPercentage');
    const validFromInput = document.getElementById('validFrom');
    const validToInput = document.getElementById('validTo');
    const updateBtn = document.getElementById('updateStudentOfferBtn');

    let errors = [];

    // Service validation
    if (servicesCheckboxes.length === 0) {
        errors.push('At least one service must be selected.');
    }

    // Discount validation
    let discountValue = discountInput ? parseFloat(discountInput.value) : NaN;
    if (isNaN(discountValue) || discountValue < 1 || discountValue > 100) {
        errors.push('Discount percentage must be between 1 and 100.');
    }

    // Date validation
    let validFromDate = validFromInput ? new Date(validFromInput.value) : null;
    let validToDate = validToInput ? new Date(validToInput.value) : null;

    if (!validFromDate || isNaN(validFromDate.getTime())) {
        errors.push('Valid From date is required.');
    }
    if (!validToDate || isNaN(validToDate.getTime())) {
        errors.push('Valid Until date is required.');
    }
    if (validFromDate && validToDate && validToDate < validFromDate) {
        errors.push('Valid Until date must be on or after Valid From date.');
    }

    // Display errors
    const errorDiv = document.getElementById('editStudentOfferFormError');
    if (errorDiv) {
        if (errors.length > 0) {
            errorDiv.innerHTML = errors.join('<br>');
            errorDiv.style.display = 'block';
        } else {
            errorDiv.style.display = 'none';
        }
    }

    // Enable/disable update button
    if (updateBtn) {
        updateBtn.disabled = errors.length > 0;
    }
}

/**
 * Update student offer preview
 */
function updateStudentOfferPreview() {
    const servicesSelect = document.getElementById('serviceIds');
    const discountInput = document.getElementById('discountPercentage');
    const validDaysSelect = document.getElementById('validDays');
    const validFromInput = document.getElementById('validFrom');
    const validToInput = document.getElementById('validTo');
    const previewDiv = document.getElementById('studentOfferPreview');

    if (servicesSelect && discountInput && discountInput.value) {
        const selectedServices = Array.from(servicesSelect.selectedOptions).map(s => s.textContent);
        const previewHTML = `
            <div class="row">
                <div class="col-md-6">
                    <strong>Services:</strong><br>
                    <ul class="mb-2">
                        ${selectedServices.map(s => `<li class="small">${s}</li>`).join('')}
                    </ul>
                </div>
                <div class="col-md-6">
                    <strong>Discount:</strong> ${discountInput.value}%<br>
                    <strong>Valid:</strong> ${validDaysSelect ? validDaysSelect.value : 'Not set'}<br>
                    <strong>Period:</strong> ${validFromInput ? validFromInput.value : ''} to ${validToInput ? validToInput.value : ''}
                </div>
            </div>
        `;
        if (previewDiv) previewDiv.innerHTML = previewHTML;
    } else {
        if (previewDiv) previewDiv.innerHTML = '<p class="text-muted">Select services and discount to see preview</p>';
    }
}

/**
 * Handle submission of the add student offer form
 */
async function handleFormSubmit(event) {
    event.preventDefault(); // Prevent default form submission

    const addForm = document.getElementById('addStudentOfferForm');
    if (!addForm) return;

    // Disable button to prevent multiple submissions
    const saveBtn = document.getElementById('saveStudentOfferBtn');
    if (saveBtn) saveBtn.disabled = true;

    const servicesSelect = document.getElementById('serviceIds');
    const offerNameInput = document.getElementById('offerName');
    const discountInput = document.getElementById('discountPercentage');
    const validDaysSelect = document.getElementById('validDays');
    const customValidDaysInput = document.getElementById('customValidDays');
    const validFromInput = document.getElementById('validFrom');
    const validToInput = document.getElementById('validTo');
    const conditionsTextarea = document.getElementById('conditions');

    // Collect selected services
    const selectedServices = servicesSelect ? Array.from(servicesSelect.selectedOptions).map(option => option.value) : [];

    // Determine valid days value
    const validDaysValue = validDaysSelect ? validDaysSelect.value : '';
    const finalValidDays = validDaysValue === 'Custom' ? (customValidDaysInput ? customValidDaysInput.value : '') : validDaysValue;

    const formData = {
        service_ids: selectedServices,
        name: offerNameInput ? offerNameInput.value : '',
        discount_percentage: discountInput ? parseFloat(discountInput.value) : 0,
        valid_days: finalValidDays,
        valid_from: validFromInput ? validFromInput.value : '',
        valid_to: validToInput ? validToInput.value : '',
        conditions: conditionsTextarea ? conditionsTextarea.value : '',
        is_active: true // Default to true as per requirement
    };

    try {
        const response = await fetch('/packages/api/student-offers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showToast('Student offer saved successfully!', 'success');
            addForm.reset(); // Clear the form
            if (typeof loadStudentOffersTable === 'function') {
                await loadStudentOffersTable(); // Refresh the table
            }
            // Close the form or redirect if necessary (implementation depends on UI)
            const addOfferModal = document.getElementById('addStudentOfferModal'); // Assuming a modal
            if (addOfferModal && typeof bootstrap !== 'undefined') {
                const modalInstance = new bootstrap.Modal(addOfferModal);
                modalInstance.hide();
            } else if (document.getElementById('addStudentOfferFormContainer')) {
                document.getElementById('addStudentOfferFormContainer').style.display = 'none'; // Hide form container
            }
            // Reset preview
            updateStudentOfferPreview();

        } else {
            throw new Error(result.error || 'Failed to save student offer. Please check your inputs.');
        }
    } catch (error) {
        console.error('Error saving student offer:', error);
        showToast('Error saving student offer: ' + error.message, 'error');
        // Display error message in the form
        const errorDiv = document.getElementById('addStudentOfferFormError');
        if (errorDiv) {
            errorDiv.innerHTML = `Error: ${error.message}`;
            errorDiv.style.display = 'block';
        }
    } finally {
        // Re-enable button
        if (saveBtn) saveBtn.disabled = false;
    }
}

/**
 * Handle submission of the edit student offer form
 */
async function handleEditFormSubmit(event) {
    event.preventDefault(); // Prevent default form submission

    const editForm = document.getElementById('editStudentOfferForm');
    if (!editForm) return;

    const offerId = document.getElementById('offerId') ? document.getElementById('offerId').value : null;
    if (!offerId) {
        showToast('Error: Offer ID not found for editing.', 'error');
        return;
    }

    // Disable button to prevent multiple submissions
    const updateBtn = document.getElementById('updateStudentOfferBtn');
    if (updateBtn) updateBtn.disabled = true;

    const servicesCheckboxes = document.querySelectorAll('input[name="service_ids"]:checked');
    const offerNameInput = document.getElementById('offerName');
    const discountInput = document.getElementById('discountPercentage');
    const validDaysSelect = document.getElementById('validDays');
    const customValidDaysInput = document.getElementById('customValidDays');
    const validFromInput = document.getElementById('validFrom');
    const validToInput = document.getElementById('validTo');
    const conditionsTextarea = document.getElementById('conditions');

    // Collect selected services
    const selectedServices = Array.from(servicesCheckboxes).map(checkbox => checkbox.value);

    // Determine valid days value
    const validDaysValue = validDaysSelect ? validDaysSelect.value : '';
    const finalValidDays = validDaysValue === 'Custom' ? (customValidDaysInput ? customValidDaysInput.value : '') : validDaysValue;

    const formData = {
        service_ids: selectedServices,
        name: offerNameInput ? offerNameInput.value : '',
        discount_percentage: discountInput ? parseFloat(discountInput.value) : 0,
        valid_days: finalValidDays,
        valid_from: validFromInput ? validFromInput.value : '',
        valid_to: validToInput ? validToInput.value : '',
        conditions: conditionsTextarea ? conditionsTextarea.value : '',
        is_active: true // Assuming active status is managed elsewhere or true by default
    };

    try {
        const response = await fetch(`/api/student-offers/${offerId}`, {
            method: 'PUT', // Use PUT for updating
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showToast('Student offer updated successfully!', 'success');
            // Redirect or close modal and refresh list
            if (typeof loadStudentOffersTable === 'function') {
                await loadStudentOffersTable(); // Refresh the table
            }
            // Redirect to the main student offers page or close modal
            window.location.href = '/packages#assign-student'; // Example redirect
        } else {
            throw new Error(result.error || 'Failed to update student offer. Please check your inputs.');
        }
    } catch (error) {
        console.error('Error updating student offer:', error);
        showToast('Error updating student offer: ' + error.message, 'error');
        // Display error message in the form
        const errorDiv = document.getElementById('editStudentOfferFormError');
        if (errorDiv) {
            errorDiv.innerHTML = `Error: ${error.message}`;
            errorDiv.style.display = 'block';
        }
    } finally {
        // Re-enable button
        if (updateBtn) updateBtn.disabled = false;
    }
}

/**
 * Edit student offer - redirect to dedicated page or handle in modal
 */
function editStudentOffer(offerId) {
    console.log('Editing student offer:', offerId);
    // Option 1: Redirect to a dedicated edit page
    window.location.href = `/student-offers/edit?id=${offerId}`;
}

/**
 * Delete student offer
 */
async function deleteStudentOffer(offerId) {
    if (!confirm('Are you sure you want to delete this student offer?')) {
        return;
    }

    try {
        const response = await fetch(`/packages/api/student-offers/${offerId}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (response.ok && (result.success || result.message)) { // Check for success or a message indicating deletion
            showToast('Student offer deleted successfully!', 'success');

            // Reload student offers if the function exists
            if (typeof loadStudentOffersTable === 'function') {
                await loadStudentOffersTable();
            }
        } else {
            throw new Error(result.error || 'Failed to delete student offer');
        }
    } catch (error) {
        console.error('Error deleting student offer:', error);
        showToast('Error deleting student offer: ' + error.message, 'error');
    }
}

/**
 * Assign student offer
 */
function assignStudentOffer(offerId) {
    console.log('Assigning student offer:', offerId);
    openAssignSimple(offerId, 'student_offer');
}

/**
 * Open assignment modal for student offers
 */
function openAssignSimple(offerId, packageType) {
    console.log('Opening assignment modal for:', offerId, packageType);
    
    // Set the offer details in the assignment modal
    const offerTypeInput = document.getElementById('assignOfferType');
    const offerIdInput = document.getElementById('assignOfferReferenceId');
    const customerSelect = document.getElementById('assignCustomerSelect');
    
    if (offerTypeInput) {
        offerTypeInput.value = packageType || 'student_offer';
    }
    
    if (offerIdInput) {
        offerIdInput.value = offerId;
    }
    
    // Load customers for assignment
    loadCustomersForAssignment();
    
    // Show the assignment modal
    const assignModal = document.getElementById('assignPackageModal');
    if (assignModal) {
        const modalInstance = new bootstrap.Modal(assignModal);
        modalInstance.show();
    } else {
        // Fallback: show simple assignment dialog
        showSimpleAssignmentDialog(offerId, packageType);
    }
}

/**
 * Load customers for assignment dropdown
 */
async function loadCustomersForAssignment() {
    try {
        const response = await fetch('/packages/api/customers');
        const data = await response.json();
        
        const customerSelect = document.getElementById('assignCustomerSelect');
        if (customerSelect && data.success && data.customers) {
            customerSelect.innerHTML = '<option value="">Choose customer...</option>';
            
            data.customers.forEach(customer => {
                const option = document.createElement('option');
                option.value = customer.id;
                option.textContent = `${customer.name} - ${customer.phone || customer.email || ''}`;
                customerSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading customers:', error);
        showToast('Error loading customers', 'error');
    }
}

/**
 * Simple assignment dialog fallback
 */
function showSimpleAssignmentDialog(offerId, packageType) {
    const customerName = prompt('Enter customer name or ID for assignment:');
    if (customerName) {
        // Try to assign directly
        assignStudentOfferToCustomer(offerId, customerName);
    }
}

/**
 * Assign student offer to customer
 */
async function assignStudentOfferToCustomer(offerId, customerId) {
    try {
        const assignmentData = {
            customer_id: customerId,
            package_id: offerId,
            package_type: 'student_offer',
            price_paid: 0.0,
            notes: 'Student offer assignment'
        };
        
        const response = await fetch('/packages/api/assign', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(assignmentData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Student offer assigned successfully!', 'success');
            // Close modal if open
            const assignModal = document.getElementById('assignPackageModal');
            if (assignModal) {
                const modalInstance = bootstrap.Modal.getInstance(assignModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }
        } else {
            throw new Error(result.error || 'Assignment failed');
        }
    } catch (error) {
        console.error('Error assigning student offer:', error);
        showToast('Error assigning student offer: ' + error.message, 'error');
    }
}

/**
 * Load student offers table
 */
async function loadStudentOffersTable() {
    try {
        const response = await fetch('/packages/api/student-offers');
        const data = await response.json();

        const tableBody = document.querySelector('#tblStudentOffers tbody');
        if (!tableBody) {
            console.error('Student offers table body not found');
            return;
        }

        tableBody.innerHTML = ''; // Clear existing rows

        if (data && data.length > 0) {
            currentStudentOffers = data;

            data.forEach(offer => {
                const row = document.createElement('tr');
                const servicesList = offer.services ? offer.services.map(s => s.name).join(', ') : 'No services';
                const validityDate = offer.valid_to || 'N/A'; // Assuming 'valid_to' is the validity date

                row.innerHTML = `
                    <td><strong>${offer.name || 'N/A'}</strong></td> {/* Display Offer Name */}
                    <td><small>${servicesList}</small></td>
                    <td><strong>${offer.discount_percentage || 'N/A'}%</strong></td> {/* Display Discount Percentage */}
                    <td><small>${validityDate}</small></td> {/* Display Validity Date */}
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

            // Update count if element exists
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

/**
 * Utility function for toast notifications
 */
function showToast(message, type = 'info') {
    // Use existing toast system if available
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
        return;
    }

    // Fallback to simple alert
    const emoji = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    alert(`${emoji} ${message}`);
}

/**
 * Confirm assignment from modal
 */
function confirmAssignment() {
    // Get values from the modal form fields
    const customerSelect = document.getElementById('assignCustomerSelect');
    const offerTypeInput = document.getElementById('assignOfferType');
    const offerIdInput = document.getElementById('assignOfferReferenceId');
    
    if (!customerSelect || !customerSelect.value) {
        showToast('Please select a customer', 'error');
        return;
    }
    
    if (!offerIdInput || !offerIdInput.value) {
        showToast('Package ID not found', 'error');
        return;
    }
    
    // Disable button during assignment
    const confirmBtn = document.getElementById('confirmAssignBtn');
    let originalText = 'Assign Package';
    if (confirmBtn) {
        originalText = confirmBtn.innerHTML;
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';
    }
    
    // Perform assignment
    const assignmentData = {
        customer_id: parseInt(customerSelect.value),
        package_id: parseInt(offerIdInput.value),
        package_type: offerTypeInput ? offerTypeInput.value : 'student_offer',
        price_paid: 0.0,
        notes: 'Student offer assignment'
    };
    
    fetch('/packages/api/assign', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(assignmentData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            showToast('Student offer assigned successfully!', 'success');
            
            // Close modal
            const assignModal = document.getElementById('assignPackageModal');
            const modalInstance = bootstrap.Modal.getInstance(assignModal);
            if (modalInstance) {
                modalInstance.hide();
            }
            
            // Reset form fields
            if (customerSelect) customerSelect.value = '';
            if (offerIdInput) offerIdInput.value = '';
            if (offerTypeInput) offerTypeInput.value = '';
        } else {
            throw new Error(result.error || 'Assignment failed');
        }
    })
    .catch(error => {
        console.error('Error assigning package:', error);
        showToast('Error assigning package: ' + error.message, 'error');
    })
    .finally(() => {
        // Restore button
        if (confirmBtn) {
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = originalText;
        }
    });
}

// Expose functions globally for onclick handlers
window.editStudentOffer = editStudentOffer;
window.deleteStudentOffer = deleteStudentOffer;
window.assignStudentOffer = assignStudentOffer;
window.openAssignSimple = openAssignSimple;
window.confirmAssignment = confirmAssignment;
window.loadStudentOffersTable = loadStudentOffersTable;

// Also expose the assignment function specifically for student offers
window.openAssignSimpleStudentOffer = function(offerId) {
    console.log('Opening assignment for student offer:', offerId);
    openAssignSimple(offerId, 'student_offer');
};

// Add missing assignPackage function for other package types
window.assignPackage = function(packageId, packageType) {
    console.log('Assigning package:', packageId, packageType);
    openAssignSimple(packageId, packageType);
};

// Ensure confirmAssignment is properly bound to the button
document.addEventListener('DOMContentLoaded', function() {
    // Bind the confirm assignment button if it exists
    const confirmBtn = document.getElementById('confirmAssignBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function(e) {
            e.preventDefault();
            confirmAssignment();
        });
    }
});