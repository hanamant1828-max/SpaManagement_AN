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
    if (document.getElementById('addStudentOfferForm') || document.getElementById('editStudentOfferForm')) {
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
 * Validate student offer form
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
    let validToDate = validToField ? new Date(validToField.value) : null;

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
 * Validate edit student offer form
 */
function validateEditStudentOfferForm() {
    const servicesSelect = document.getElementById('editStudentOfferServices');
    const discountInput = document.getElementById('editStudentDiscountPercentage');
    const validFromInput = document.getElementById('editStudentValidFrom');
    const validToInput = document.getElementById('editStudentValidTo');
    const updateBtn = document.getElementById('updateStudentOffer');

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
    let validToDate = validToField ? new Date(validToField.value) : null;

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
        const response = await fetch('/api/student-offers', {
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

    const offerId = editForm.dataset.offerId; // Assuming offerId is stored in a data attribute
    if (!offerId) {
        showToast('Error: Offer ID not found for editing.', 'error');
        return;
    }

    // Disable button to prevent multiple submissions
    const updateBtn = document.getElementById('updateStudentOffer');
    if (updateBtn) updateBtn.disabled = true;

    const servicesSelect = document.getElementById('editStudentOfferServices');
    const offerNameInput = document.getElementById('editOfferName');
    const discountInput = document.getElementById('editStudentDiscountPercentage');
    const validDaysSelect = document.getElementById('editStudentValidDays');
    const customValidDaysInput = document.getElementById('editCustomValidDays');
    const validFromInput = document.getElementById('editStudentValidFrom');
    const validToInput = document.getElementById('editStudentValidTo');
    const conditionsTextarea = document.getElementById('editStudentConditions');

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
            window.location.href = '/student-offers'; // Example redirect
            // Or if in a modal:
            // const editOfferModal = document.getElementById('editStudentOfferModal'); // Assuming a modal
            // if (editOfferModal && typeof bootstrap !== 'undefined') {
            //     const modalInstance = new bootstrap.Modal(editOfferModal);
            //     modalInstance.hide();
            // }
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

    // Option 2: Load data into an edit modal (if using modals)
    // fetch(`/api/student-offers/${offerId}`)
    //     .then(response => response.json())
    //     .then(offer => {
    //         if (offer.success) {
    //             populateEditForm(offer.offer); // Function to populate the modal form
    //             const editOfferModal = document.getElementById('editStudentOfferModal');
    //             if (editOfferModal && typeof bootstrap !== 'undefined') {
    //                 const modalInstance = new bootstrap.Modal(editOfferModal);
    //                 editOfferModal.dataset.offerId = offerId; // Store offerId for submission
    //                 modalInstance.show();
    //             }
    //         } else {
    //             throw new Error(offer.error || 'Failed to load offer details.');
    //         }
    //     })
    //     .catch(error => {
    //         console.error('Error loading offer for edit:', error);
    //         showToast('Error loading offer details: ' + error.message, 'error');
    //     });
}

/**
 * Delete student offer
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
    // Use the existing assignment system
    if (typeof openAssignSimple === 'function') {
        openAssignSimple(offerId, 'student_offer');
    } else {
        showToast('Assignment feature coming soon!', 'info');
    }
}

/**
 * Load student offers table
 */
async function loadStudentOffersTable() {
    try {
        const response = await fetch('/api/student-offers');
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
                const validPeriod = `${offer.valid_from} to ${offer.valid_to}`;

                row.innerHTML = `
                    <td><strong>${offer.discount_percentage}%</strong></td>
                    <td><small>${servicesList}</small></td>
                    <td>${offer.valid_days}</td>
                    <td><small>${validPeriod}</small></td>
                    <td><small>${offer.conditions || 'No conditions'}</small></td>
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

// Expose functions globally for onclick handlers
window.editStudentOffer = editStudentOffer;
window.deleteStudentOffer = deleteStudentOffer;
window.assignStudentOffer = assignStudentOffer;
window.loadStudentOffersTable = loadStudentOffersTable;