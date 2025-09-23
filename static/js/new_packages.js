/**
 * Student Offer Management JavaScript Functions
 * Handles Add, Edit, Delete, and Assignment operations
 */

// Global functions for student offer management
window.editStudentOffer = function(offerId) {
    console.log('Edit student offer:', offerId);
    if (typeof loadStudentOfferForEdit === 'function') {
        loadStudentOfferForEdit(offerId);
    } else {
        alert('Edit functionality coming soon');
    }
};

window.deleteStudentOffer = function(offerId) {
    if (!confirm('Are you sure you want to delete this student offer?')) {
        return;
    }

    fetch(`/api/student-offers/${offerId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Student offer deleted successfully!');
            if (typeof loadStudentPackages === 'function') {
                loadStudentPackages();
            } else {
                location.reload();
            }
        } else {
            alert('Error deleting student offer: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error deleting student offer');
    });
};

window.assignStudentOffer = function(offerId) {
    console.log('Assign student offer:', offerId);
    if (typeof openAssignSimple === 'function') {
        openAssignSimple(offerId, 'student');
    } else {
        alert('Assignment functionality coming soon');
    }
};

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
                        <td><strong>${offer.name || 'Student Offer'}</strong></td>
                        <td><small>${serviceNames}</small></td>
                        <td><span class="badge bg-success">${offer.discount_percentage}%</span></td>
                        <td>
                            <small>
                                <strong>From:</strong> ${offer.valid_from}<br>
                                <strong>To:</strong> ${offer.valid_to}
                            </small>
                        </td>
                        <td><span class="badge bg-info">${offer.valid_days}</span></td>
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

// Edit student offer - redirect to dedicated edit page
function editStudentOffer(offerId) {
    console.log('Editing student offer:', offerId);
    window.location.href = `/packages/student-offers/edit?id=${offerId}`;
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

    // Initialize student offer modals
    initializeStudentOfferModals();
});



// Assignment functionality
function submitAssignment() {
    console.log('Submitting package assignment...');

    const form = document.getElementById('assignPackageForm');
    if (!form) {
        console.error('Assignment form not found');
        return;
    }

    const formData = new FormData(form);
    const assignmentData = {
        customer_id: formData.get('customer_id'),
        package_type: formData.get('offer_type'),
        package_id: formData.get('offer_reference_id'),
        price_paid: parseFloat(formData.get('custom_price')) || 0,
        notes: formData.get('notes') || ''
    };

    if (!assignmentData.customer_id) {
        alert('Please select a customer');
        return;
    }

    // Show loading state
    const submitBtn = document.querySelector('#assignPackageModal .btn-primary');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Assigning...';

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
            alert('Package assigned successfully!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignPackageModal'));
            modal.hide();
            form.reset();
        } else {
            alert('Error assigning package: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error assigning package:', error);
        alert('Error assigning package. Please try again.');
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    });
}

// Additional utility functions for package assignment
function openAssignSimple(packageId, packageType) {
    console.log('Opening assign modal for:', packageType, packageId);

    document.getElementById('assignOfferType').value = packageType;
    document.getElementById('assignOfferReferenceId').value = packageId;

    const assignModal = new bootstrap.Modal(document.getElementById('assignPackageModal'));
    assignModal.show();
}