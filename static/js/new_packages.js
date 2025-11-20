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

// Assign student offer - redirect to assign packages page
window.assignStudentOffer = function(offerId) {
    console.log('Assigning student offer:', offerId);
    // Redirect to assign packages page with pre-selected student offer
    window.location.href = `/assign-packages/?package_type=student_offer&package_id=${offerId}`;
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
                const price = offer.price ? `₹${parseFloat(offer.price).toFixed(2)}` : '₹0.00';
                const row = `
                    <tr>
                        <td><strong>${offer.name || 'Student Offer'}</strong></td>
                        <td><small>${serviceNames}</small></td>
                        <td><strong>${price}</strong></td>
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

// Edit prepaid package
window.editPrepaid = function(packageId) {
    console.log('Edit prepaid package:', packageId);

    fetch(`/api/prepaid-packages/${packageId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Prepaid package data received:', data);
            if (data && data.success && data.id) {
                // Populate edit modal fields
                document.getElementById('editPrepaidId').value = data.id;
                document.getElementById('editPrepaidName').value = data.name || '';
                document.getElementById('editPrepaidActualPrice').value = data.actual_price || 0;
                document.getElementById('editPrepaidAfterValue').value = data.after_value || 0;
                document.getElementById('editPrepaidBenefitPercent').value = data.benefit_percent || 0;
                document.getElementById('editPrepaidValidityMonths').value = data.validity_months || 12;

                // Show edit modal
                const editModal = new bootstrap.Modal(document.getElementById('editPrepaidModal'));
                editModal.show();
            } else {
                alert('Error: ' + (data.error || 'Package data not found'));
            }
        })
        .catch(error => {
            console.error('Error loading prepaid package:', error);
            alert('Error loading prepaid package details: ' + error.message);
        });
};

// Update prepaid package
window.updatePrepaid = function() {
    const packageId = document.getElementById('editPrepaidId').value;
    const formData = {
        name: document.getElementById('editPrepaidName').value,
        actual_price: parseFloat(document.getElementById('editPrepaidActualPrice').value),
        after_value: parseFloat(document.getElementById('editPrepaidAfterValue').value),
        benefit_percent: parseFloat(document.getElementById('editPrepaidBenefitPercent').value),
        validity_months: parseInt(document.getElementById('editPrepaidValidityMonths').value),
        is_active: true
    };

    fetch(`/api/prepaid-packages/${packageId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Prepaid package updated successfully!');
            location.reload();
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating prepaid package');
    });
};

// Delete prepaid package
window.deletePrepaid = function(packageId) {
    if (!confirm('Are you sure you want to delete this prepaid package?')) return;

    fetch(`/api/prepaid-packages/${packageId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Prepaid package deleted successfully!');
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting prepaid package');
        });
};

// Edit service package
window.editService = function(packageId) {
    console.log('Editing service:', packageId);

    fetch(`/api/service-packages/${packageId}`)
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Service data received:', data);
            if (data && data.id) {
                // Check if edit modal exists
                const editModal = document.getElementById('editServiceModal');
                if (!editModal) {
                    console.error('Edit service modal not found in DOM');
                    alert('Edit modal not found. Please refresh the page.');
                    return;
                }

                // Safely populate edit modal fields
                const fields = {
                    'editServiceId': data.id,
                    'editServiceName': data.name,
                    'editServicePayFor': data.pay_for,
                    'editServiceFreeServices': data.free_services,
                    'editServiceValidityMonths': data.validity_months
                };

                for (const [fieldId, value] of Object.entries(fields)) {
                    const field = document.getElementById(fieldId);
                    if (field) {
                        field.value = value || '';
                    } else {
                        console.warn(`Field ${fieldId} not found in edit modal`);
                    }
                }

                // Show modal
                const modal = new bootstrap.Modal(editModal);
                modal.show();
            } else {
                alert('Service package data not found');
            }
        })
        .catch(error => {
            console.error('Error loading service package:', error);
            alert('Error loading service package details: ' + error.message);
        });
};

// Update service package
window.updateService = function() {
    const packageId = document.getElementById('editServiceId').value;
    const formData = {
        name: document.getElementById('editServiceName').value,
        pay_for: parseInt(document.getElementById('editServicePayFor').value),
        free_services: parseInt(document.getElementById('editServiceFreeServices').value),
        validity_months: parseInt(document.getElementById('editServiceValidityMonths').value),
        is_active: true
    };

    fetch(`/api/service-packages/${packageId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Service package updated successfully!');
            location.reload();
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating service package');
    });
};

// Delete service package
window.deleteService = function(packageId) {
    if (!confirm('Are you sure you want to delete this service package?')) return;

    fetch(`/api/service-packages/${packageId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Service package deleted successfully!');
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting service package');
        });
};

// Edit yearly membership
window.editYearly = function(membershipId) {
    console.log('Edit yearly membership:', membershipId);

    fetch(`/api/yearly-memberships/${membershipId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.membership) {
                const membership = data.membership;
                document.getElementById('editYearlyId').value = membership.id;
                document.getElementById('editYearlyName').value = membership.name;
                document.getElementById('editYearlyPrice').value = membership.price;
                document.getElementById('editYearlyDiscountPercent').value = membership.discount_percent;
                document.getElementById('editYearlyValidityMonths').value = membership.validity_months;
                document.getElementById('editYearlyExtraBenefits').value = membership.extra_benefits || '';

                const editModal = new bootstrap.Modal(document.getElementById('editYearlyModal'));
                editModal.show();
            }
        })
        .catch(error => {
            console.error('Error loading yearly membership:', error);
            alert('Error loading yearly membership details');
        });
};

// Update yearly membership
window.updateYearly = function() {
    const membershipId = document.getElementById('editYearlyId').value;
    const formData = {
        name: document.getElementById('editYearlyName').value,
        price: parseFloat(document.getElementById('editYearlyPrice').value),
        discount_percent: parseFloat(document.getElementById('editYearlyDiscountPercent').value),
        validity_months: parseInt(document.getElementById('editYearlyValidityMonths').value),
        extra_benefits: document.getElementById('editYearlyExtraBenefits').value,
        is_active: true
    };

    fetch(`/api/yearly-memberships/${membershipId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Yearly membership updated successfully!');
            location.reload();
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating yearly membership');
    });
};

// Delete yearly membership
window.deleteYearly = function(membershipId) {
    if (!confirm('Are you sure you want to delete this yearly membership?')) return;

    fetch(`/api/yearly-memberships/${membershipId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Yearly membership deleted successfully!');
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting yearly membership');
        });
};

// Edit kitty party
window.editKitty = function(partyId) {
    console.log('Edit kitty party:', partyId);

    fetch(`/api/kitty-parties/${partyId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.party) {
                const party = data.party;
                document.getElementById('editKittyId').value = party.id;
                document.getElementById('editKittyName').value = party.name;
                document.getElementById('editKittyPrice').value = party.price;
                document.getElementById('editKittyMinGuests').value = party.min_guests;
                document.getElementById('editKittyValidityMonths').value = party.validity_months;
                document.getElementById('editKittyInclusions').value = party.inclusions || '';

                const editModal = new bootstrap.Modal(document.getElementById('editKittyModal'));
                editModal.show();
            }
        })
        .catch(error => {
            console.error('Error loading kitty party:', error);
            alert('Error loading kitty party details');
        });
};

// Update kitty party
window.updateKitty = function() {
    const partyId = document.getElementById('editKittyId').value;
    const formData = {
        name: document.getElementById('editKittyName').value,
        price: parseFloat(document.getElementById('editKittyPrice').value),
        min_guests: parseInt(document.getElementById('editKittyMinGuests').value),
        validity_months: parseInt(document.getElementById('editKittyValidityMonths').value),
        inclusions: document.getElementById('editKittyInclusions').value,
        is_active: true
    };

    fetch(`/api/kitty-parties/${partyId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('Kitty party updated successfully!');
            location.reload();
        } else {
            alert('Error: ' + (result.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating kitty party');
    });
};

// Delete kitty party
window.deleteKitty = function(partyId) {
    if (!confirm('Are you sure you want to delete this kitty party?')) return;

    fetch(`/api/kitty-parties/${partyId}`, { method: 'DELETE' })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert('Kitty party deleted successfully!');
                location.reload();
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error deleting kitty party');
        });
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('Student offers JavaScript loaded');

    // Load student packages if on the right tab
    if (document.getElementById('tblStudentOffers')) {
        loadStudentPackages();
    }
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

// Assign membership to customer
window.assignMembershipToCustomer = function(membershipId) {
    console.log('Assign membership to customer:', membershipId);
    // Redirect to assign packages page
    window.location.href = '/assign-packages/';
};

// Save Yearly Membership function
window.saveYearlyMembership = function() {
    console.log('Saving yearly membership...');

    const form = document.getElementById('yearlyForm');
    if (!form) {
        console.error('Yearly membership form not found');
        alert('Form not found. Please refresh the page and try again.');
        return;
    }

    const formData = new FormData(form);

    const membershipData = {
        name: formData.get('name'),
        price: parseFloat(formData.get('price')),
        discount_percent: parseFloat(formData.get('discount_percent')),
        validity_months: parseInt(formData.get('validity_months')),
        extra_benefits: formData.get('extra_benefits') || ''
    };

    if (!membershipData.name || !membershipData.price || !membershipData.discount_percent || !membershipData.validity_months) {
        alert('Please fill in all required fields');
        return;
    }

    const saveBtn = document.getElementById('saveYearlyMembershipBtn');
    const originalText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Saving...';

    fetch('/api/yearly-memberships', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(membershipData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success || data.id) {
            alert('Yearly membership saved successfully!');
            const modal = bootstrap.Modal.getInstance(document.getElementById('yearlyModal'));
            if (modal) {
                modal.hide();
            }
            form.reset();

            if (typeof loadYearlyPackages === 'function') {
                loadYearlyPackages();
            } else {
                location.reload();
            }
        } else {
            alert('Error saving yearly membership: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error saving yearly membership:', error);
        alert('Error saving yearly membership. Please try again.');
    })
    .finally(() => {
        saveBtn.disabled = false;
        saveBtn.innerHTML = originalText;
    });
};

function openKittyPartyModal() {
    const modal = new bootstrap.Modal(document.getElementById('addKittyPartyModal'));
    modal.show();

    // Load services for the kitty party immediately
    setTimeout(() => loadServicesForKittyParty(), 100);
}

function loadServicesForKittyParty() {
    const servicesContainer = document.getElementById('kittyPartyServices');
    if (!servicesContainer) {
        console.warn('Kitty party services container not found');
        return;
    }

    console.log('Loading services for Kitty Party...');
    servicesContainer.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-spinner fa-spin me-2"></i>Loading services...</div>';

    fetch('/api/services')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(services => {
            console.log(`Loaded ${services.length} services for Kitty Party`);

            if (services && services.length > 0) {
                const servicesHTML = services.map(service => `
                    <div class="form-check mb-2">
                        <input class="form-check-input" type="checkbox" name="service_ids" value="${service.id}" id="kitty_service_${service.id}">
                        <label class="form-check-label" for="kitty_service_${service.id}">
                            <strong>${service.name}</strong> - <span class="text-success">$${service.price.toFixed(2)}</span>
                        </label>
                    </div>
                `).join('');

                servicesContainer.innerHTML = `
                    <div class="mb-2 text-muted small">Select multiple services for this kitty party</div>
                    ${servicesHTML}
                `;
            } else {
                servicesContainer.innerHTML = '<div class="alert alert-warning mb-0"><i class="fas fa-exclamation-triangle me-2"></i>No services available. Please add services first.</div>';
            }
        })
        .catch(error => {
            console.error('Error loading services:', error);
            servicesContainer.innerHTML = `<div class="alert alert-danger mb-0"><i class="fas fa-exclamation-circle me-2"></i>Error loading services: ${error.message}</div>`;
        });
}