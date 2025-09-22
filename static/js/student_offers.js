
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
    initializeStudentOffers();
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
    
    if (validFromField) validFromField.value = today;
    if (validToField) validToField.value = futureDate;
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
                addSelect.innerHTML = '';
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
                editSelect.innerHTML = '';
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
    // Add form validation
    const addForm = document.getElementById('addStudentOfferForm');
    if (addForm) {
        addForm.addEventListener('input', validateStudentOfferForm);
        addForm.addEventListener('change', validateStudentOfferForm);
    }

    // Edit form validation
    const editForm = document.getElementById('editStudentOfferForm');
    if (editForm) {
        editForm.addEventListener('input', validateEditStudentOfferForm);
        editForm.addEventListener('change', validateEditStudentOfferForm);
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

    // Save button event listeners
    const saveBtn = document.getElementById('saveStudentOfferBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveStudentOffer);
    }

    const updateBtn = document.getElementById('updateStudentOffer');
    if (updateBtn) {
        updateBtn.addEventListener('click', updateStudentOffer);
    }
}

/**
 * Validate student offer form
 */
function validateStudentOfferForm() {
    const services = document.getElementById('serviceIds');
    const discount = document.getElementById('discountPercentage');
    const validFrom = document.getElementById('validFrom');
    const validTo = document.getElementById('validTo');
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

/**
 * Validate edit student offer form
 */
function validateEditStudentOfferForm() {
    const services = document.getElementById('editStudentOfferServices');
    const discount = document.getElementById('editStudentDiscountPercentage');
    const validFrom = document.getElementById('editStudentValidFrom');
    const validTo = document.getElementById('editStudentValidTo');
    const updateBtn = document.getElementById('updateStudentOffer');

    const isValid = services && services.selectedOptions.length > 0 && 
                   discount && discount.value && parseFloat(discount.value) >= 1 && parseFloat(discount.value) <= 100 &&
                   validFrom && validFrom.value && validTo && validTo.value && 
                   new Date(validTo.value) > new Date(validFrom.value);

    if (updateBtn) {
        updateBtn.disabled = !isValid;
    }
}

/**
 * Update student offer preview
 */
function updateStudentOfferPreview() {
    const services = document.getElementById('serviceIds');
    const discount = document.getElementById('discountPercentage');
    const validDays = document.getElementById('validDays');
    const validFrom = document.getElementById('validFrom');
    const validTo = document.getElementById('validTo');
    const preview = document.getElementById('studentOfferPreview');

    if (services && services.selectedOptions.length > 0 && discount && discount.value) {
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
                    <strong>Valid:</strong> ${validDays ? validDays.value : 'Not set'}<br>
                    <strong>Period:</strong> ${validFrom ? validFrom.value : ''} to ${validTo ? validTo.value : ''}
                </div>
            </div>
        `;
        preview.innerHTML = previewHTML;
    } else {
        preview.innerHTML = '<p class="text-muted">Select services and discount to see preview</p>';
    }
}

/**
 * Save student offer (for dedicated pages, not modal)
 */
async function saveStudentOffer() {
    try {
        // This function is now primarily used by the dedicated add/edit pages
        // The modal-based saving is handled within those pages
        console.log('Student offer save function called');
    } catch (error) {
        console.error('Error in saveStudentOffer:', error);
    }
}

/**
 * Edit student offer - open edit modal or redirect to dedicated page
 */
function editStudentOffer(offerId) {
    // Check if we have a dedicated edit page route
    if (typeof window.location !== 'undefined') {
        // Try to open edit modal first, fallback to page redirect
        const editModal = document.getElementById('editStudentOfferModal');
        if (editModal) {
            // Load student offer data and show modal
            loadStudentOfferForEdit(offerId);
        } else {
            // Redirect to edit page if modal not available
            window.location.href = `/packages/student-offers/edit?id=${offerId}`;
        }
    }
}

/**
 * Load student offer data for editing
 */
async function loadStudentOfferForEdit(offerId) {
    try {
        const response = await fetch(`/api/student-offers/${offerId}`);
        const data = await response.json();

        if (data.success && data.offer) {
            const offer = data.offer;
            
            // Populate edit form
            document.getElementById('editOfferId').value = offer.id;
            document.getElementById('editStudentDiscountPercentage').value = offer.discount_percentage;
            document.getElementById('editStudentValidFrom').value = offer.valid_from ? offer.valid_from.split('T')[0] : '';
            document.getElementById('editStudentValidTo').value = offer.valid_to ? offer.valid_to.split('T')[0] : '';
            document.getElementById('editStudentConditions').value = offer.conditions || '';

            // Handle valid days
            const standardDays = ['Mon-Fri', 'Mon-Sat', 'All Days', 'Weekends'];
            if (standardDays.includes(offer.valid_days)) {
                document.getElementById('editStudentValidDays').value = offer.valid_days;
            } else {
                document.getElementById('editStudentValidDays').value = 'Custom';
                document.getElementById('editCustomValidDaysDiv').style.display = 'block';
                document.getElementById('editCustomValidDays').value = offer.valid_days;
            }

            // Select services
            const servicesSelect = document.getElementById('editStudentOfferServices');
            if (servicesSelect && offer.services) {
                Array.from(servicesSelect.options).forEach(option => {
                    option.selected = offer.services.some(service => service.id == option.value);
                });
            }

            // Show the modal
            const modal = new bootstrap.Modal(document.getElementById('editStudentOfferModal'));
            modal.show();
        } else {
            throw new Error(data.error || 'Student offer not found');
        }
    } catch (error) {
        console.error('Error loading student offer:', error);
        showToast('Error loading student offer: ' + error.message, 'error');
    }
}

/**
 * Update student offer
 */
async function updateStudentOffer() {
    try {
        const form = document.getElementById('editStudentOfferForm');
        const formData = new FormData(form);
        const offerId = document.getElementById('editOfferId').value;

        // Handle valid days
        const validDaysSelect = document.getElementById('editStudentValidDays');
        const customValidDays = document.getElementById('editCustomValidDays');
        if (validDaysSelect.value === 'Custom' && customValidDays.value) {
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

        // Show loading state
        const updateBtn = document.getElementById('updateStudentOffer');
        const originalText = updateBtn.innerHTML;
        updateBtn.disabled = true;
        updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Updating...';

        const response = await fetch(`/api/student-offers/${offerId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success || response.ok) {
            showToast('Student offer updated successfully!', 'success');

            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentOfferModal'));
            modal.hide();

            // Reload student offers if the function exists
            if (typeof loadStudentPackages === 'function') {
                await loadStudentPackages();
            }
        } else {
            throw new Error(result.error || 'Failed to update student offer');
        }
    } catch (error) {
        console.error('Error updating student offer:', error);
        showToast('Error updating student offer: ' + error.message, 'error');
    } finally {
        // Restore button state
        const updateBtn = document.getElementById('updateStudentOffer');
        if (updateBtn) {
            updateBtn.disabled = false;
            updateBtn.innerHTML = '<i class="fas fa-save me-2"></i>Update Student Offer';
        }
    }
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

        if (result.success || response.ok) {
            showToast('Student offer deleted successfully!', 'success');
            
            // Reload student offers if the function exists
            if (typeof loadStudentPackages === 'function') {
                await loadStudentPackages();
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

        tableBody.innerHTML = '';

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
