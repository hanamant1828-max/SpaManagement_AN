/**
 * Student Offer Management JavaScript Functions
 * Handles Add, Edit, Delete, and Assignment operations
 */

// Load student packages data
function loadStudentPackages() {
    console.log('Loading student packages...');
    
    fetch('/api/student-offers')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('tblStudentOffers');
            if (!tbody) {
                console.error('Student offers table not found');
                return;
            }
            
            tbody.innerHTML = '';
            
            data.forEach(offer => {
                const serviceNames = offer.services ? offer.services.map(s => s.name).join(', ') : 'No services';
                const row = `
                    <tr>
                        <td>${serviceNames}</td>
                        <td>₹${parseFloat(offer.services?.[0]?.price || 0).toLocaleString()}</td>
                        <td>${offer.discount_percentage}%</td>
                        <td>₹${(parseFloat(offer.services?.[0]?.price || 0) * (1 - offer.discount_percentage/100)).toLocaleString()}</td>
                        <td class="text-success">₹${(parseFloat(offer.services?.[0]?.price || 0) * (offer.discount_percentage/100)).toLocaleString()}</td>
                        <td>${offer.valid_days}</td>
                        <td>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-success btn-sm" onclick="assignStudentOffer(${offer.id})" title="Assign to Customer">
                                    <i class="fas fa-user-plus"></i> Assign
                                </button>
                                <button class="btn btn-outline-primary" onclick="editStudentOffer(${offer.id})" title="Edit Offer">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteStudentOffer(${offer.id})" title="Delete Offer">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
            
            console.log(`Loaded ${data.length} student offers`);
        })
        .catch(error => {
            console.error('Error loading student packages:', error);
        });
}

// Edit student offer
function editStudentOffer(offerId) {
    console.log('Editing student offer:', offerId);
    
    fetch(`/api/student-offers/${offerId}`)
        .then(response => response.json())
        .then(offer => {
            // Populate edit form
            document.getElementById('editStudentOfferId').value = offer.id;
            document.getElementById('editDiscountPercentage').value = offer.discount_percentage;
            document.getElementById('editValidFrom').value = offer.valid_from;
            document.getElementById('editValidTo').value = offer.valid_to;
            document.getElementById('editValidDays').value = offer.valid_days;
            document.getElementById('editConditions').value = offer.conditions;
            
            // Set selected services in multi-select
            const serviceSelect = document.getElementById('editServiceIds');
            if (serviceSelect && offer.services) {
                Array.from(serviceSelect.options).forEach(option => {
                    option.selected = offer.services.some(s => s.id == option.value);
                });
            }
            
            // Show edit modal
            const editModal = new bootstrap.Modal(document.getElementById('editStudentOfferModal'));
            editModal.show();
        })
        .catch(error => {
            console.error('Error loading student offer for edit:', error);
        });
}

// Delete student offer
function deleteStudentOffer(offerId) {
    console.log('Deleting student offer:', offerId);
    
    if (!confirm('Are you sure you want to delete this student offer?')) {
        return;
    }
    
    fetch(`/api/student-offers/${offerId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Student offer deleted successfully!');
            loadStudentPackages(); // Reload the table
        } else {
            alert('Error deleting student offer: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error deleting student offer:', error);
        alert('Error deleting student offer');
    });
}

// Assign student offer to customer
function assignStudentOffer(offerId) {
    console.log('Assigning student offer:', offerId);
    
    // Set the offer ID in the assignment modal
    document.getElementById('assignOfferType').value = 'student_offer';
    document.getElementById('assignOfferReferenceId').value = offerId;
    
    // Show assignment modal
    const assignModal = new bootstrap.Modal(document.getElementById('assignPackageModal'));
    assignModal.show();
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Student offers JavaScript loaded');
    
    // Load student packages if on the right tab
    if (document.getElementById('tblStudentOffers')) {
        loadStudentPackages();
    }
    
    // Handle add student offer form submission
    const addForm = document.getElementById('addStudentOfferForm');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const selectedServices = Array.from(document.getElementById('serviceIds').selectedOptions)
                .map(option => option.value);
            
            // Add selected services to form data
            selectedServices.forEach(serviceId => {
                formData.append('service_ids', serviceId);
            });
            
            fetch('/api/student-offers', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Student offer created successfully!');
                    addForm.reset();
                    const modal = bootstrap.Modal.getInstance(document.getElementById('addStudentOfferModal'));
                    modal.hide();
                    loadStudentPackages();
                } else {
                    alert('Error creating student offer: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error creating student offer:', error);
                alert('Error creating student offer');
            });
        });
    }
    
    // Handle edit student offer form submission
    const editForm = document.getElementById('editStudentOfferForm');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const offerId = document.getElementById('editStudentOfferId').value;
            const selectedServices = Array.from(document.getElementById('editServiceIds').selectedOptions)
                .map(option => option.value);
            
            // Add selected services to form data
            selectedServices.forEach(serviceId => {
                formData.append('service_ids', serviceId);
            });
            
            fetch(`/api/student-offers/${offerId}`, {
                method: 'PUT',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Student offer updated successfully!');
                    const modal = bootstrap.Modal.getInstance(document.getElementById('editStudentOfferModal'));
                    modal.hide();
                    loadStudentPackages();
                } else {
                    alert('Error updating student offer: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error updating student offer:', error);
                alert('Error updating student offer');
            });
        });
    }
});

// Additional utility functions for package assignment
function openAssignSimple(packageId, packageType) {
    console.log('Opening assign modal for:', packageType, packageId);
    
    document.getElementById('assignOfferType').value = packageType;
    document.getElementById('assignOfferReferenceId').value = packageId;
    
    const assignModal = new bootstrap.Modal(document.getElementById('assignPackageModal'));
    assignModal.show();
}