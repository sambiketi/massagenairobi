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
            if (e.target.classList.contains('modal-overlay')) {
                closeBookingModal();
            }
        });
    }
    
    // Set default date to tomorrow
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = tomorrow.toISOString().split('T')[0];
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
    
    if (serviceId) {
        document.getElementById('serviceId').value = serviceId;
    }
    if (therapistId) {
        document.getElementById('therapistId').value = therapistId;
    }
    
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
    
    const formData = new FormData(event.target);
    const bookingData = {
        name: formData.get('clientName'),
        phone: formData.get('clientPhone'),
        email: formData.get('clientEmail'),
        service_id: formData.get('serviceId') || null,
        therapist_id: formData.get('therapistId') || null,
        date: formData.get('appointmentDate'),
        time: formData.get('appointmentTime'),
        mpesa_code: formData.get('mpesaCode') || 'PENDING_TILL',
        notes: formData.get('notes') || ''
    };
    
    // Show loading state
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
    submitBtn.disabled = true;
    
    try {
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(bookingData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Open WhatsApp with confirmation
            if (result.whatsapp_url) {
                window.open(result.whatsapp_url, '_blank');
            }
            
            showToast('Booking confirmed! Please check WhatsApp for details.', 'success');
            closeBookingModal();
            event.target.reset();
        } else {
            showToast('Booking failed: ' + (result.error || 'Please try again'), 'error');
        }
    } catch (error) {
        console.error('Booking error:', error);
        showToast('An error occurred. Please try again.', 'error');
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Toast Notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        toast.style.transition = 'all 0.3s ease';
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