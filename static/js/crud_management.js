
// Global variables
let currentModule = '';
let currentAction = '';
let currentItemId = null;
let allData = {
    categories: [],
    locations: [],
    products: [],
    customers: []
};

// Form templates for each module
const formTemplates = {
    category: `
        <div class="form-section">
            <h6 class="mb-3"><i class="fas fa-info-circle me-2"></i>Basic Information</h6>
            <div class="row">
                <div class="col-md-6">
                    <label for="name" class="form-label">Name *</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                    <div class="invalid-feedback">Please provide a category name.</div>
                </div>
                <div class="col-md-6">
                    <label for="display_name" class="form-label">Display Name *</label>
                    <input type="text" class="form-control" id="display_name" name="display_name" required>
                    <div class="invalid-feedback">Please provide a display name.</div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="category_type" class="form-label">Type *</label>
                    <select class="form-select" id="category_type" name="category_type" required>
                        <option value="">Select type...</option>
                        <option value="service">Service</option>
                        <option value="product">Product</option>
                        <option value="expense">Expense</option>
                        <option value="other">Other</option>
                    </select>
                    <div class="invalid-feedback">Please select a category type.</div>
                </div>
                <div class="col-md-6">
                    <label for="color" class="form-label">Color</label>
                    <input type="color" class="form-control form-control-color" id="color" name="color" value="#007bff">
                </div>
            </div>
            <div class="mt-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" name="description" rows="3"></textarea>
            </div>
            <div class="mt-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="is_active" name="is_active" checked>
                    <label class="form-check-label" for="is_active">Active</label>
                </div>
            </div>
        </div>
    `,
    
    location: `
        <div class="form-section">
            <h6 class="mb-3"><i class="fas fa-info-circle me-2"></i>Location Details</h6>
            <div class="row">
                <div class="col-md-8">
                    <label for="name" class="form-label">Location Name *</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                    <div class="invalid-feedback">Please provide a location name.</div>
                </div>
                <div class="col-md-4">
                    <label for="manager_id" class="form-label">Manager</label>
                    <select class="form-select" id="manager_id" name="manager_id">
                        <option value="">Select manager...</option>
                    </select>
                </div>
            </div>
            <div class="mt-3">
                <label for="address" class="form-label">Address *</label>
                <textarea class="form-control" id="address" name="address" rows="3" required></textarea>
                <div class="invalid-feedback">Please provide an address.</div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="phone" class="form-label">Phone</label>
                    <input type="tel" class="form-control" id="phone" name="phone">
                </div>
                <div class="col-md-6">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email">
                </div>
            </div>
            <div class="mt-3">
                <label for="operating_hours" class="form-label">Operating Hours</label>
                <textarea class="form-control" id="operating_hours" name="operating_hours" rows="2" placeholder="Mon-Fri: 9:00 AM - 8:00 PM"></textarea>
            </div>
            <div class="mt-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="is_active" name="is_active" checked>
                    <label class="form-check-label" for="is_active">Active</label>
                </div>
            </div>
        </div>
    `,
    
    product: `
        <div class="form-section">
            <h6 class="mb-3"><i class="fas fa-box me-2"></i>Product Information</h6>
            <div class="row">
                <div class="col-md-6">
                    <label for="sku" class="form-label">SKU *</label>
                    <input type="text" class="form-control" id="sku" name="sku" required>
                    <div class="invalid-feedback">Please provide a SKU.</div>
                </div>
                <div class="col-md-6">
                    <label for="name" class="form-label">Product Name *</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                    <div class="invalid-feedback">Please provide a product name.</div>
                </div>
            </div>
            <div class="mt-3">
                <label for="description" class="form-label">Description</label>
                <textarea class="form-control" id="description" name="description" rows="3"></textarea>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="category_id" class="form-label">Category</label>
                    <select class="form-select" id="category_id" name="category_id">
                        <option value="">Select category...</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <label for="supplier_id" class="form-label">Supplier</label>
                    <select class="form-select" id="supplier_id" name="supplier_id">
                        <option value="">Select supplier...</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="form-section">
            <h6 class="mb-3"><i class="fas fa-warehouse me-2"></i>Inventory & Pricing</h6>
            <div class="row">
                <div class="col-md-4">
                    <label for="current_stock" class="form-label">Current Stock</label>
                    <input type="number" class="form-control" id="current_stock" name="current_stock" min="0" step="0.01" value="0">
                </div>
                <div class="col-md-4">
                    <label for="min_stock_level" class="form-label">Min Stock Level</label>
                    <input type="number" class="form-control" id="min_stock_level" name="min_stock_level" min="0" step="0.01" value="10">
                </div>
                <div class="col-md-4">
                    <label for="unit_of_measure" class="form-label">Unit</label>
                    <select class="form-select" id="unit_of_measure" name="unit_of_measure">
                        <option value="pcs">Pieces</option>
                        <option value="kg">Kilograms</option>
                        <option value="liters">Liters</option>
                        <option value="boxes">Boxes</option>
                    </select>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="cost_price" class="form-label">Cost Price</label>
                    <input type="number" class="form-control" id="cost_price" name="cost_price" min="0" step="0.01" value="0">
                </div>
                <div class="col-md-6">
                    <label for="selling_price" class="form-label">Selling Price</label>
                    <input type="number" class="form-control" id="selling_price" name="selling_price" min="0" step="0.01" value="0">
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="barcode" class="form-label">Barcode</label>
                    <input type="text" class="form-control" id="barcode" name="barcode">
                </div>
                <div class="col-md-6">
                    <label for="location" class="form-label">Storage Location</label>
                    <input type="text" class="form-control" id="location" name="location">
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="is_service_item" name="is_service_item">
                        <label class="form-check-label" for="is_service_item">Used in Services</label>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="is_retail_item" name="is_retail_item">
                        <label class="form-check-label" for="is_retail_item">Retail Item</label>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="is_active" name="is_active" checked>
                    <label class="form-check-label" for="is_active">Active</label>
                </div>
            </div>
        </div>
    `,
    
    customer: `
        <div class="form-section">
            <h6 class="mb-3"><i class="fas fa-user me-2"></i>Personal Information</h6>
            <div class="row">
                <div class="col-md-6">
                    <label for="first_name" class="form-label">First Name *</label>
                    <input type="text" class="form-control" id="first_name" name="first_name" required>
                    <div class="invalid-feedback">Please provide a first name.</div>
                </div>
                <div class="col-md-6">
                    <label for="last_name" class="form-label">Last Name *</label>
                    <input type="text" class="form-control" id="last_name" name="last_name" required>
                    <div class="invalid-feedback">Please provide a last name.</div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email">
                </div>
                <div class="col-md-6">
                    <label for="phone" class="form-label">Phone *</label>
                    <input type="tel" class="form-control" id="phone" name="phone" required>
                    <div class="invalid-feedback">Please provide a phone number.</div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="date_of_birth" class="form-label">Date of Birth</label>
                    <input type="date" class="form-control" id="date_of_birth" name="date_of_birth">
                </div>
                <div class="col-md-6">
                    <label for="gender" class="form-label">Gender</label>
                    <select class="form-select" id="gender" name="gender">
                        <option value="">Select...</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                    </select>
                </div>
            </div>
            <div class="mt-3">
                <label for="address" class="form-label">Address</label>
                <textarea class="form-control" id="address" name="address" rows="3"></textarea>
            </div>
        </div>
        <div class="form-section">
            <h6 class="mb-3"><i class="fas fa-notes-medical me-2"></i>Additional Information</h6>
            <div class="row">
                <div class="col-md-6">
                    <label for="allergies" class="form-label">Allergies</label>
                    <textarea class="form-control" id="allergies" name="allergies" rows="2"></textarea>
                </div>
                <div class="col-md-6">
                    <label for="preferences" class="form-label">Preferences</label>
                    <textarea class="form-control" id="preferences" name="preferences" rows="2"></textarea>
                </div>
            </div>
            <div class="mt-3">
                <label for="notes" class="form-label">Notes</label>
                <textarea class="form-control" id="notes" name="notes" rows="3"></textarea>
            </div>
            <div class="row mt-3">
                <div class="col-md-6">
                    <label for="preferred_communication" class="form-label">Preferred Communication</label>
                    <select class="form-select" id="preferred_communication" name="preferred_communication">
                        <option value="email">Email</option>
                        <option value="sms">SMS</option>
                        <option value="whatsapp">WhatsApp</option>
                        <option value="phone">Phone</option>
                    </select>
                </div>
                <div class="col-md-6">
                    <div class="form-check mt-4">
                        <input class="form-check-input" type="checkbox" id="marketing_consent" name="marketing_consent" checked>
                        <label class="form-check-label" for="marketing_consent">Marketing Consent</label>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="is_active" name="is_active" checked>
                    <label class="form-check-label" for="is_active">Active</label>
                </div>
            </div>
        </div>
    `
};

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    console.log('CRUD Management System loaded');
    loadAllData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Form submission
    document.getElementById('crudForm').addEventListener('submit', handleFormSubmit);
    
    // Delete confirmation
    document.getElementById('confirmDeleteBtn').addEventListener('click', handleDelete);
    
    // Modal cleanup
    document.getElementById('crudModal').addEventListener('hidden.bs.modal', function() {
        resetForm();
    });
}

// Load all data
async function loadAllData() {
    await Promise.all([
        loadModuleData('categories'),
        loadModuleData('locations'),
        loadModuleData('products'),
        loadModuleData('customers')
    ]);
}

// Load data for a specific module
async function loadModuleData(module) {
    try {
        showLoading(module, true);
        const response = await fetch(`/api/crud/${module}`);
        const data = await response.json();
        
        if (data.success) {
            allData[module] = data.data;
            updateModuleDisplay(module);
            showNotification(`${capitalizeFirst(module)} loaded successfully`, 'success');
        } else {
            throw new Error(data.error || `Failed to load ${module}`);
        }
    } catch (error) {
        console.error(`Error loading ${module}:`, error);
        showNotification(`Error loading ${module}: ${error.message}`, 'error');
        showEmptyState(module);
    } finally {
        showLoading(module, false);
    }
}

// Update module display
function updateModuleDisplay(module) {
    const data = allData[module];
    const countElement = document.getElementById(`${module}Count`);
    const tableBody = document.getElementById(`${module}TableBody`);
    
    countElement.textContent = data.length;
    
    if (data.length === 0) {
        showEmptyState(module);
        return;
    }
    
    let rows = '';
    data.forEach(item => {
        rows += generateTableRow(module, item);
    });
    
    tableBody.innerHTML = rows;
}

// Generate table row for each module
function generateTableRow(module, item) {
    switch (module) {
        case 'categories':
            return `
                <tr>
                    <td>${item.display_name || item.name}</td>
                    <td><span class="badge bg-secondary badge-status">${item.category_type}</span></td>
                    <td><span class="badge ${item.is_active ? 'bg-success' : 'bg-danger'} badge-status">${item.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-outline-primary btn-action" onclick="openEditModal('category', ${item.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="openDeleteModal('category', ${item.id}, '${item.name}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        case 'locations':
            return `
                <tr>
                    <td>${item.name}</td>
                    <td>${item.manager_name || 'Not assigned'}</td>
                    <td><span class="badge ${item.is_active ? 'bg-success' : 'bg-danger'} badge-status">${item.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-outline-primary btn-action" onclick="openEditModal('location', ${item.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="openDeleteModal('location', ${item.id}, '${item.name}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        case 'products':
            return `
                <tr>
                    <td><code>${item.sku}</code></td>
                    <td>${item.name}</td>
                    <td>$${parseFloat(item.selling_price || 0).toFixed(2)}</td>
                    <td>
                        <button class="btn btn-outline-primary btn-action" onclick="openEditModal('product', ${item.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="openDeleteModal('product', ${item.id}, '${item.name}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        case 'customers':
            return `
                <tr>
                    <td>${item.first_name} ${item.last_name}</td>
                    <td>${item.phone || 'N/A'}</td>
                    <td><span class="badge ${item.is_active ? 'bg-success' : 'bg-danger'} badge-status">${item.is_active ? 'Active' : 'Inactive'}</span></td>
                    <td>
                        <button class="btn btn-outline-primary btn-action" onclick="openEditModal('customer', ${item.id})" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger btn-action" onclick="openDeleteModal('customer', ${item.id}, '${item.first_name} ${item.last_name}')" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        default:
            return '';
    }
}

// Open add modal
function openAddModal(module) {
    currentModule = module;
    currentAction = 'add';
    currentItemId = null;
    
    const modal = new bootstrap.Modal(document.getElementById('crudModal'));
    document.getElementById('modalTitle').innerHTML = `<i class="fas fa-plus me-2"></i>Add ${capitalizeFirst(module)}`;
    document.getElementById('modalBody').innerHTML = formTemplates[module];
    
    // Populate dropdowns if needed
    populateDropdowns(module);
    
    modal.show();
}

// Open edit modal
async function openEditModal(module, id) {
    currentModule = module;
    currentAction = 'edit';
    currentItemId = id;
    
    const modal = new bootstrap.Modal(document.getElementById('crudModal'));
    document.getElementById('modalTitle').innerHTML = `<i class="fas fa-edit me-2"></i>Edit ${capitalizeFirst(module)}`;
    document.getElementById('modalBody').innerHTML = formTemplates[module];
    
    // Populate dropdowns if needed
    populateDropdowns(module);
    
    // Load current data
    try {
        const response = await fetch(`/api/crud/${module}/${id}`);
        const data = await response.json();
        
        if (data.success) {
            populateForm(data.data);
        } else {
            throw new Error(data.error || 'Failed to load item data');
        }
    } catch (error) {
        console.error('Error loading item data:', error);
        showNotification('Error loading item data', 'error');
        return;
    }
    
    modal.show();
}

// Open delete modal
function openDeleteModal(module, id, name) {
    currentModule = module;
    currentItemId = id;
    
    document.getElementById('deleteItemType').textContent = module.slice(0, -1); // Remove 's' from plural
    document.querySelector('#deleteModal .modal-body p').innerHTML = 
        `Are you sure you want to delete <strong>${name}</strong>?`;
    
    const modal = new bootstrap.Modal(document.getElementById('deleteModal'));
    modal.show();
}

// Populate form dropdowns
async function populateDropdowns(module) {
    if (module === 'location') {
        // Load managers for location form
        try {
            const response = await fetch('/api/crud/managers');
            const data = await response.json();
            if (data.success) {
                const managerSelect = document.getElementById('manager_id');
                managerSelect.innerHTML = '<option value="">Select manager...</option>';
                data.data.forEach(manager => {
                    managerSelect.innerHTML += `<option value="${manager.id}">${manager.first_name} ${manager.last_name}</option>`;
                });
            }
        } catch (error) {
            console.error('Error loading managers:', error);
        }
    } else if (module === 'product') {
        // Load categories and suppliers for product form
        try {
            const [categoriesRes, suppliersRes] = await Promise.all([
                fetch('/api/crud/categories'),
                fetch('/api/crud/suppliers')
            ]);
            
            const categoriesData = await categoriesRes.json();
            const suppliersData = await suppliersRes.json();
            
            if (categoriesData.success) {
                const categorySelect = document.getElementById('category_id');
                categorySelect.innerHTML = '<option value="">Select category...</option>';
                categoriesData.data.forEach(category => {
                    if (category.category_type === 'product') {
                        categorySelect.innerHTML += `<option value="${category.id}">${category.display_name || category.name}</option>`;
                    }
                });
            }
            
            if (suppliersData.success) {
                const supplierSelect = document.getElementById('supplier_id');
                supplierSelect.innerHTML = '<option value="">Select supplier...</option>';
                suppliersData.data.forEach(supplier => {
                    supplierSelect.innerHTML += `<option value="${supplier.id}">${supplier.name}</option>`;
                });
            }
        } catch (error) {
            console.error('Error loading dropdown data:', error);
        }
    }
}

// Populate form with existing data
function populateForm(data) {
    Object.keys(data).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            if (element.type === 'checkbox') {
                element.checked = data[key];
            } else {
                element.value = data[key] || '';
            }
        }
    });
}

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    const formData = new FormData(event.target);
    const data = {};
    
    // Convert FormData to object
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    // Handle checkboxes (they won't be in FormData if unchecked)
    const checkboxes = event.target.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        data[checkbox.name] = checkbox.checked;
    });
    
    // Show loading state
    const submitBtn = document.getElementById('submitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Saving...';
    
    try {
        const url = currentAction === 'add' ? 
            `/api/crud/${currentModule}` : 
            `/api/crud/${currentModule}/${currentItemId}`;
        
        const method = currentAction === 'add' ? 'POST' : 'PUT';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`${capitalizeFirst(currentModule.slice(0, -1))} ${currentAction === 'add' ? 'added' : 'updated'} successfully!`, 'success');
            
            // Refresh the module data
            await loadModuleData(currentModule);
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('crudModal')).hide();
        } else {
            throw new Error(result.error || `Failed to ${currentAction} ${currentModule.slice(0, -1)}`);
        }
    } catch (error) {
        console.error(`Error ${currentAction}ing ${currentModule.slice(0, -1)}:`, error);
        showNotification(`Error ${currentAction}ing ${currentModule.slice(0, -1)}: ${error.message}`, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// Handle delete
async function handleDelete() {
    const deleteBtn = document.getElementById('confirmDeleteBtn');
    const originalText = deleteBtn.innerHTML;
    deleteBtn.disabled = true;
    deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Deleting...';
    
    try {
        const response = await fetch(`/api/crud/${currentModule}/${currentItemId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`${capitalizeFirst(currentModule.slice(0, -1))} deleted successfully!`, 'success');
            
            // Refresh the module data
            await loadModuleData(currentModule);
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('deleteModal')).hide();
        } else {
            throw new Error(result.error || `Failed to delete ${currentModule.slice(0, -1)}`);
        }
    } catch (error) {
        console.error(`Error deleting ${currentModule.slice(0, -1)}:`, error);
        showNotification(`Error deleting ${currentModule.slice(0, -1)}: ${error.message}`, 'error');
    } finally {
        deleteBtn.disabled = false;
        deleteBtn.innerHTML = originalText;
    }
}

// Form validation
function validateForm() {
    const form = document.getElementById('crudForm');
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
        }
    });
    
    // Additional validation
    if (currentModule === 'customer') {
        const email = document.getElementById('email');
        if (email.value && !isValidEmail(email.value)) {
            email.classList.add('is-invalid');
            isValid = false;
        }
    }
    
    return isValid;
}

// Email validation
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Reset form
function resetForm() {
    const form = document.getElementById('crudForm');
    form.reset();
    form.classList.remove('was-validated');
    
    // Remove validation classes
    const inputs = form.querySelectorAll('.is-valid, .is-invalid');
    inputs.forEach(input => {
        input.classList.remove('is-valid', 'is-invalid');
    });
}

// Show loading state
function showLoading(module, show) {
    const loadingElement = document.getElementById(`${module}Loading`);
    if (loadingElement) {
        loadingElement.style.display = show ? 'flex' : 'none';
    }
}

// Show empty state
function showEmptyState(module) {
    const tableBody = document.getElementById(`${module}TableBody`);
    const colCount = tableBody.closest('table').querySelectorAll('thead th').length;
    
    tableBody.innerHTML = `
        <tr>
            <td colspan="${colCount}" class="text-center text-muted py-4">
                <i class="fas fa-inbox fa-2x mb-2 d-block"></i>
                No ${module} found. Click "Add ${capitalizeFirst(module.slice(0, -1))}" to get started.
            </td>
        </tr>
    `;
}

// Show notification
function showNotification(message, type = 'info', duration = 5000) {
    const container = document.getElementById('notificationContainer');
    
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    };
    
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass[type] || 'alert-info'} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        if (notification && notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

// Utility function
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}
