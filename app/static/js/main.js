// Handle Booking Form Submission
async function handleBookingSubmit(event) {
    event.preventDefault();
    
    // Get form data directly from HTML elements
    const bookingData = {
        client_name: document.getElementById('clientName').value.trim(),
        client_phone: document.getElementById('clientPhone').value.trim(),
        service_id: document.getElementById('serviceId').value,  // ← FIXED: Use hidden input
        appointment_date: document.getElementById('appointmentDate').value,
        appointment_time: document.getElementById('appointmentTime').value,
        notes: document.getElementById('notes').value.trim()
    };
    
    // Validate required fields
    if (!bookingData.client_name) {
        showError('Please enter your full name.');
        return;
    }
    if (!bookingData.client_phone) {
        showError('Please enter your phone number.');
        return;
    }
    if (!bookingData.service_id) {
        showError('No service selected. Please go back and select a service.');
        return;
    }
    if (!bookingData.appointment_date) {
        showError('Please select a date.');
        return;
    }
    if (!bookingData.appointment_time) {
        showError('Please select a time.');
        return;
    }
    
    console.log('📤 Sending booking data:', bookingData);
    
    // Show loading state
    const submitBtn = document.getElementById('bookingSubmit');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    submitBtn.disabled = true;
    
    // Hide previous messages
    document.getElementById('bookingError').classList.add('hidden');
    document.getElementById('bookingSuccess').classList.add('hidden');
    
    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        console.log('📥 API response:', result);
        
        if (result.success) {
            const successDiv = document.getElementById('bookingSuccess');
            successDiv.textContent = '✅ ' + (result.message || 'Booking confirmed! We will contact you shortly.');
            successDiv.classList.remove('hidden');
            
            if (result.whatsapp_url) {
                setTimeout(() => {
                    window.open(result.whatsapp_url, '_blank');
                }, 500);
            }
            
            // Reset form after success
            setTimeout(() => {
                closeBookingModal();
                const form = document.getElementById('bookingForm');
                if (form) {
                    form.reset();
                    // Reset date to tomorrow
                    const tomorrow = new Date();
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    document.getElementById('appointmentDate').value = tomorrow.toISOString().split('T')[0];
                    document.getElementById('appointmentTime').value = '14:00';
                }
            }, 3000);
        } else {
            showError(result.error || 'Booking failed. Please try again.');
        }
    } catch (error) {
        console.error('❌ Booking error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Show Error Message
function showError(message) {
    const errorDiv = document.getElementById('bookingError');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    document.getElementById('bookingSuccess').classList.add('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}