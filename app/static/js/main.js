// ============================================================
// MAIN.JS - Complete Website Functionality
// ============================================================

// ============================================================
// BOOKING MODAL FUNCTIONS
// ============================================================

/**
 * Open the booking modal
 * @param {string|null} serviceId - Optional service ID to pre-select
 */
function openBookingModal(serviceId = null) {
    const modal = document.getElementById('bookingModal');
    if (!modal) {
        console.error('Booking modal not found');
        return;
    }
    
    const serviceIdInput = document.getElementById('serviceId');
    const displaySelect = document.getElementById('bookingServiceDisplay');
    const errorDiv = document.getElementById('bookingError');
    const successDiv = document.getElementById('bookingSuccess');
    
    // Clear previous messages
    if (errorDiv) errorDiv.classList.add('hidden');
    if (successDiv) successDiv.classList.add('hidden');
    
    // Set the service ID if provided
    if (serviceId && serviceIdInput) {
        serviceIdInput.value = serviceId;
        
        // Sync the display dropdown
        if (displaySelect) {
            displaySelect.value = serviceId;
        }
        
        console.log('📌 Service pre-selected:', serviceId);
    } else if (serviceIdInput) {
        serviceIdInput.value = '';
        if (displaySelect) {
            displaySelect.value = '';
        }
    }
    
    // Set default date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput && !dateInput.value) {
        dateInput.value = tomorrow.toISOString().split('T')[0];
    }
    
    // Set default time
    const timeInput = document.getElementById('appointmentTime');
    if (timeInput && !timeInput.value) {
        timeInput.value = '14:00';
    }
    
    // Show the modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

/**
 * Close the booking modal
 */
function closeBookingModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.add('hidden');
    }
    document.body.style.overflow = '';
    
    // Reset form
    const form = document.getElementById('bookingForm');
    if (form) {
        form.reset();
    }
}

/**
 * Handle booking form submission
 * @param {Event} event - Form submit event
 */
async function handleBookingSubmit(event) {
    event.preventDefault();
    
    // Get form data
    const bookingData = {
        client_name: document.getElementById('clientName')?.value.trim() || '',
        client_phone: document.getElementById('clientPhone')?.value.trim() || '',
        service_id: document.getElementById('serviceId')?.value || '',
        appointment_date: document.getElementById('appointmentDate')?.value || '',
        appointment_time: document.getElementById('appointmentTime')?.value || '',
        notes: document.getElementById('notes')?.value.trim() || ''
    };
    
    // Validate required fields
    if (!bookingData.client_name) {
        showError('Please enter your full name.');
        document.getElementById('clientName')?.focus();
        return;
    }
    
    if (bookingData.client_name.length < 2) {
        showError('Please enter a valid name (minimum 2 characters).');
        document.getElementById('clientName')?.focus();
        return;
    }
    
    if (!bookingData.client_phone) {
        showError('Please enter your phone number.');
        document.getElementById('clientPhone')?.focus();
        return;
    }
    
    if (bookingData.client_phone.length < 7) {
        showError('Please enter a valid phone number (minimum 7 digits).');
        document.getElementById('clientPhone')?.focus();
        return;
    }
    
    if (!bookingData.service_id) {
        showError('No service selected. Please go back and select a service.');
        return;
    }
    
    if (!bookingData.appointment_date) {
        showError('Please select a date.');
        document.getElementById('appointmentDate')?.focus();
        return;
    }
    
    if (!bookingData.appointment_time) {
        showError('Please select a time.');
        document.getElementById('appointmentTime')?.focus();
        return;
    }
    
    // Validate date is not in the past
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDate = new Date(bookingData.appointment_date);
    if (selectedDate < today) {
        showError('Please select a date in the future.');
        document.getElementById('appointmentDate')?.focus();
        return;
    }
    
    console.log('📤 Sending booking data:', bookingData);
    
    // Show loading state
    const submitBtn = document.getElementById('bookingSubmit');
    const originalText = submitBtn?.innerHTML || 'Confirm Booking';
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        submitBtn.disabled = true;
    }
    
    // Hide previous messages
    const errorDiv = document.getElementById('bookingError');
    const successDiv = document.getElementById('bookingSuccess');
    if (errorDiv) errorDiv.classList.add('hidden');
    if (successDiv) successDiv.classList.add('hidden');
    
    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        console.log('📥 API response:', result);
        
        if (result.success) {
            // Show success message
            if (successDiv) {
                successDiv.textContent = '✅ ' + (result.message || 'Booking confirmed! We will contact you shortly.');
                successDiv.classList.remove('hidden');
            }
            
            // Open WhatsApp if URL provided
            if (result.whatsapp_url) {
                setTimeout(() => {
                    window.open(result.whatsapp_url, '_blank');
                }, 500);
            }
            
            // Close modal after delay
            setTimeout(() => {
                closeBookingModal();
                // Reset form
                const form = document.getElementById('bookingForm');
                if (form) {
                    form.reset();
                }
            }, 3000);
        } else {
            // Show error from server
            const errorMsg = result.error || 'Booking failed. Please try again.';
            if (result.missing) {
                showError(`Missing fields: ${result.missing.join(', ')}`);
            } else {
                showError(errorMsg);
            }
        }
    } catch (error) {
        console.error('❌ Booking error:', error);
        showError('Network error. Please check your connection and try again.');
    } finally {
        // Restore button
        if (submitBtn) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    const errorDiv = document.getElementById('bookingError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }
    
    const successDiv = document.getElementById('bookingSuccess');
    if (successDiv) {
        successDiv.classList.add('hidden');
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
    }, 5000);
}

// ============================================================
// NAVBAR TOGGLE (Mobile)
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Close mobile menu on link click
    const mobileLinks = document.querySelectorAll('#mobileMenu a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (mobileMenu) {
                mobileMenu.classList.add('hidden');
            }
        });
    });
    
    // Auto-close booking modal on ESC key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeBookingModal();
        }
    });
    
    // Click outside modal to close
    const modalOverlay = document.querySelector('.modal-overlay');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function() {
            closeBookingModal();
        });
    }
    
    // Set min date for appointment date picker
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.min = tomorrow.toISOString().split('T')[0];
    }
    
    console.log('✅ Main.js loaded successfully');
});

// ============================================================
// SMOOTH SCROLL FOR ANCHOR LINKS
// ============================================================

document.addEventListener('click', function(event) {
    const target = event.target.closest('a[href^="#"]');
    if (target) {
        const targetId = target.getAttribute('href');
        if (targetId && targetId !== '#') {
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                event.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }
    }
});

// ============================================================
// LAZY LOADING IMAGES
// ============================================================

if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.remove('opacity-0');
                imageObserver.unobserve(img);
            }
        });
    });
    
    lazyImages.forEach(function(img) {
        imageObserver.observe(img);
    });
}

// ============================================================
// CONTACT FORM HANDLING (if exists)
// ============================================================

const contactForm = document.getElementById('contactForm');
if (contactForm) {
    contactForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        
        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value.trim();
        });
        
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn?.innerHTML || 'Send Message';
        
        if (submitBtn) {
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Sending...';
            submitBtn.disabled = true;
        }
        
        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('✅ Message sent successfully! We will get back to you soon.');
                this.reset();
            } else {
                alert('❌ Error: ' + (result.error || 'Failed to send message.'));
            }
        } catch (error) {
            console.error('Contact form error:', error);
            alert('❌ Network error. Please try again.');
        } finally {
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        }
    });
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

/**
 * Format currency in KES
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return 'KES ' + Number(amount).toLocaleString('en-KE', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

/**
 * Get today's date in YYYY-MM-DD format
 * @returns {string} Today's date
 */
function getTodayDate() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Get tomorrow's date in YYYY-MM-DD format
 * @returns {string} Tomorrow's date
 */
function getTomorrowDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
}

// ============================================================
// EXPOSE FUNCTIONS GLOBALLY (if needed)
// ============================================================

// Make functions available globally for inline onclick handlers
window.openBookingModal = openBookingModal;
window.closeBookingModal = closeBookingModal;
window.handleBookingSubmit = handleBookingSubmit;
window.showError = showError;
window.formatCurrency = formatCurrency;

console.log('✅ All functions loaded and ready');