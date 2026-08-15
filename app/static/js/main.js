// Booking Modal Management
let bookingModal = null;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize booking modal
    bookingModal = document.getElementById('bookingModal');
    
    // Mobile menu toggle
    const mobileToggle = document.getElementById('mobileMenuToggle');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Close modal on backdrop click
    if (bookingModal) {
        bookingModal.addEventListener('click', function(e) {
            if (e.target.id === 'bookingModal' || e.target.classList.contains('absolute')) {
                closeBookingModal();
            }
        });
    }
    
    // Set default date to tomorrow
    const dateInput = document.getElementById('bookingDate');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = tomorrow.toISOString().split('T')[0];
    }
    
    // Set default time to 2:00 PM
    const timeInput = document.getElementById('bookingTime');
    if (timeInput) {
        timeInput.value = '14:00';
    }
    
    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
});

// Open Booking Modal
function openBookingModal(serviceId = null, therapistId = null) {
    if (!bookingModal) {
        bookingModal = document.getElementById('bookingModal');
    }
    
    // If serviceId is provided, pre-select the service
    if (serviceId) {
        const serviceSelect = document.getElementById('bookingService');
        if (serviceSelect) {
            serviceSelect.value = serviceId;
        }
    }
    
    // Reset form and hide messages
    const form = document.getElementById('bookingForm');
    if (form) {
        form.reset();
        
        // Reset default date and time after reset
        const dateInput = document.getElementById('bookingDate');
        if (dateInput) {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            dateInput.value = tomorrow.toISOString().split('T')[0];
        }
        
        const timeInput = document.getElementById('bookingTime');
        if (timeInput) {
            timeInput.value = '14:00';
        }
    }
    
    // Hide error and success messages
    document.getElementById('bookingError').classList.add('hidden');
    document.getElementById('bookingSuccess').classList.add('hidden');
    
    bookingModal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

// Close Booking Modal
function closeBookingModal() {
    if (bookingModal) {
        bookingModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

// Handle Booking Form Submission
async function handleBookingSubmit(event) {
    event.preventDefault();
    
    // Get form data directly from HTML elements
    const bookingData = {
        client_name: document.getElementById('bookingName').value.trim(),
        client_phone: document.getElementById('bookingPhone').value.trim(),
        service_id: document.getElementById('bookingService').value,
        appointment_date: document.getElementById('bookingDate').value,
        appointment_time: document.getElementById('bookingTime').value,
        notes: document.getElementById('bookingNotes').value.trim()
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
        showError('Please select a service.');
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
    
    // Debug logging
    console.log('Sending booking data:', bookingData);
    
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
        console.log('API response:', result);
        
        if (result.success) {
            // Show success message
            const successDiv = document.getElementById('bookingSuccess');
            successDiv.textContent = '✅ ' + (result.message || 'Booking confirmed!');
            successDiv.classList.remove('hidden');
            
            // Open WhatsApp with confirmation
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
                }
            }, 3000);
        } else {
            showError(result.error || 'Booking failed. Please try again.');
        }
    } catch (error) {
        console.error('Booking error:', error);
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

// Show Success Message
function showSuccess(message) {
    const successDiv = document.getElementById('bookingSuccess');
    successDiv.textContent = message;
    successDiv.classList.remove('hidden');
    document.getElementById('bookingError').classList.add('hidden');
}

// Toast Notification (for non-modal messages)
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.padding = '12px 24px';
    toast.style.borderRadius = '8px';
    toast.style.color = 'white';
    toast.style.backgroundColor = type === 'success' ? '#10B981' : '#EF4444';
    toast.style.zIndex = '9999';
    toast.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
    toast.style.transition = 'opacity 0.3s ease';
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Image Upload Preview
function previewImage(input, previewElementId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById(previewElementId);
            if (preview) {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// WhatsApp Integration
function sendWhatsAppMessage(phone, message) {
    const encodedMessage = encodeURIComponent(message);
    window.open(`https://wa.me/${phone}?text=${encodedMessage}`, '_blank');
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && bookingModal && !bookingModal.classList.contains('hidden')) {
        closeBookingModal();
    }
});

// Attach form submit handler
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('bookingForm');
    if (form) {
        form.addEventListener('submit', handleBookingSubmit);
    }
});