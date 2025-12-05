
// Multi-Appointment Booking - Edit Mode Data Binding

document.addEventListener('DOMContentLoaded', function() {
    console.log('[MULTI-BOOKING] Initializing multi-appointment booking page', '');
    
    // Check if we're in edit mode
    const editDataElement = document.getElementById('editAppointmentData');
    if (editDataElement) {
        try {
            const editAppointment = JSON.parse(editDataElement.textContent);
            console.log('[MULTI-BOOKING] Edit mode enabled for appointment:', editAppointment);
            console.log('🔧 EDIT MODE ACTIVATED - Appointment ID:', editAppointment.id);
            
            // Populate the form with existing appointment data
            populateEditForm(editAppointment);
        } catch (e) {
            console.error('[MULTI-BOOKING] Error parsing edit appointment data:', e);
        }
    }
});

function populateEditForm(appointment) {
    console.log('Populating edit form with customer data:', appointment);
    
    // Wait for DOM to be ready
    setTimeout(() => {
        // 1. Select the customer
        const clientSelect = document.getElementById('clientSelect');
        if (clientSelect && appointment.client_id) {
            clientSelect.value = appointment.client_id;
            
            // Trigger change event to load customer appointments
            const event = new Event('change', { bubbles: true });
            clientSelect.dispatchEvent(event);
            
            console.log('[MULTI-BOOKING] Client selected:', appointment.client_id);
        }
        
        // 2. Set booking source
        const bookingSourceSelect = document.querySelector('select[name="booking_source"]');
        if (bookingSourceSelect && appointment.booking_source) {
            bookingSourceSelect.value = appointment.booking_source;
        }
        
        // 3. Populate the first appointment row with data
        setTimeout(() => {
            const firstAppointment = document.querySelector('.appointment-row');
            if (firstAppointment) {
                // Set service
                const serviceSelect = firstAppointment.querySelector('.service-select');
                if (serviceSelect && appointment.service_id) {
                    serviceSelect.value = appointment.service_id;
                    serviceSelect.dispatchEvent(new Event('change', { bubbles: true }));
                }
                
                // Set staff
                const staffSelect = firstAppointment.querySelector('.staff-select');
                if (staffSelect && appointment.staff_id) {
                    staffSelect.value = appointment.staff_id;
                }
                
                // Set date
                const dateInput = firstAppointment.querySelector('.appointment-date');
                if (dateInput && appointment.appointment_date) {
                    dateInput.value = appointment.appointment_date;
                }
                
                // Set start time
                const startTimeInput = firstAppointment.querySelector('.start-time-input');
                if (startTimeInput && appointment.start_time) {
                    startTimeInput.value = appointment.start_time;
                }
                
                // Set end time
                const endTimeInput = firstAppointment.querySelector('.end-time-input');
                if (endTimeInput && appointment.end_time) {
                    endTimeInput.value = appointment.end_time;
                }
                
                // Set notes
                const notesTextarea = document.getElementById('bookingNotes');
                if (notesTextarea && appointment.notes) {
                    notesTextarea.value = appointment.notes;
                }
                
                console.log('[MULTI-BOOKING] ✅ Edit form populated successfully');
            }
        }, 500);
    }, 300);
}
