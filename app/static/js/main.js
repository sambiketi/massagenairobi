// ============================================================
// MAIN.JS - Complete Website Functionality WITH DEBUG
// ============================================================

console.log('🚀 ===== MAIN.JS LOADED =====');
console.log('📍 Page URL:', window.location.href);
console.log('📍 Timestamp:', new Date().toISOString());

// ============================================================
// BOOKING MODAL FUNCTIONS
// ============================================================

/**
 * Open the booking modal
 * @param {string|null} serviceId - Optional service ID to pre-select
 */
function openBookingModal(serviceId = null) {
    console.log('🔍 ===== openBookingModal CALLED =====');
    console.log('📌 serviceId parameter:', serviceId);
    console.log('📌 serviceId type:', typeof serviceId);
    console.log('📌 serviceId length:', serviceId?.length || 0);
    console.log('📌 serviceId is null/undefined:', serviceId === null || serviceId === undefined);
    console.log('📌 serviceId is empty string:', serviceId === '');
    
    const modal = document.getElementById('bookingModal');
    const serviceIdInput = document.getElementById('serviceId');
    const displaySelect = document.getElementById('bookingServiceDisplay');
    
    // DEBUG: Check if elements exist
    console.log('📋 DOM Elements:');
    console.log('  modal:', modal ? '✅ Found' : '❌ NOT FOUND');
    console.log('  serviceIdInput:', serviceIdInput ? '✅ Found' : '❌ NOT FOUND');
    console.log('  displaySelect:', displaySelect ? '✅ Found' : '❌ NOT FOUND');
    
    if (!modal || !serviceIdInput) {
        console.error('❌ Required elements not found!');
        console.error('  modal exists:', !!modal);
        console.error('  serviceIdInput exists:', !!serviceIdInput);
        return;
    }
    
    // Clear previous messages
    const errorDiv = document.getElementById('bookingError');
    const successDiv = document.getElementById('bookingSuccess');
    if (errorDiv) errorDiv.classList.add('hidden');
    if (successDiv) successDiv.classList.add('hidden');
    
    // ============================================================
    // FIX: Try to get service ID from multiple sources
    // ============================================================
    let finalServiceId = serviceId;
    
    // If serviceId is null, undefined, or empty string, try to get it from the dropdown
    if (!finalServiceId || finalServiceId === '') {
        console.log('⚠️ No serviceId provided, checking dropdown...');
        if (displaySelect && displaySelect.value) {
            finalServiceId = displaySelect.value;
            console.log('✅ Found serviceId in dropdown:', finalServiceId);
        } else {
            console.warn('⚠️ No serviceId found in dropdown either');
        }
    }
    
    // If still no serviceId, try to get it from the URL or data attribute
    if (!finalServiceId || finalServiceId === '') {
        console.log('⚠️ Checking for service ID in URL parameters...');
        const urlParams = new URLSearchParams(window.location.search);
        const urlServiceId = urlParams.get('service');
        if (urlServiceId) {
            finalServiceId = urlServiceId;
            console.log('✅ Found serviceId in URL:', finalServiceId);
        }
    }
    
    // Set the service ID if provided
    if (finalServiceId && finalServiceId !== '') {
        serviceIdInput.value = finalServiceId;
        console.log('✅ Set serviceIdInput.value to:', serviceIdInput.value);
        
        // Sync the display dropdown
        if (displaySelect) {
            displaySelect.value = finalServiceId;
            console.log('✅ Set displaySelect.value to:', displaySelect.value);
        }
    } else {
        serviceIdInput.value = '';
        console.warn('⚠️ No serviceId found anywhere, cleared value');
        if (displaySelect) {
            displaySelect.value = '';
        }
    }
    
    // Verify the value was set
    console.log('🔍 After setting, serviceIdInput.value =', serviceIdInput.value);
    console.log('🔍 After setting, serviceIdInput.value type:', typeof serviceIdInput.value);
    console.log('🔍 After setting, serviceIdInput.value length:', serviceIdInput.value.length);
    
    // Set default date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput && !dateInput.value) {
        dateInput.value = tomorrow.toISOString().split('T')[0];
        console.log('📅 Set default date to:', dateInput.value);
    }
    
    // Set default time
    const timeInput = document.getElementById('appointmentTime');
    if (timeInput && !timeInput.value) {
        timeInput.value = '14:00';
        console.log('🕐 Set default time to:', timeInput.value);
    }
    
    // Show the modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    console.log('✅ Modal opened successfully');
    console.log('🏁 ===== openBookingModal COMPLETE =====');
    
    // If service ID is still empty, show a warning
    if (!serviceIdInput.value) {
        console.warn('⚠️⚠️⚠️ WARNING: service_id is still empty!');
        console.warn('Please check that your "Book Now" buttons have: onclick="openBookingModal(\'{{ service.id }}\')"');
        console.warn('And that {{ service.id }} is actually being rendered.');
    }
}

/**
 * Close the booking modal
 */
function closeBookingModal() {
    console.log('🔍 closeBookingModal called');
    
    const modal = document.getElementById('bookingModal');
    if (modal) {
        modal.classList.add('hidden');
        console.log('✅ Modal closed');
    } else {
        console.warn('⚠️ Modal not found');
    }
    
    document.body.style.overflow = '';
    
    // Reset form
    const form = document.getElementById('bookingForm');
    if (form) {
        form.reset();
        console.log('✅ Form reset');
    }
}

/**
 * Handle booking form submission with FULL DEBUG
 */
async function handleBookingSubmit(event) {
    event.preventDefault();
    
    console.log('🚀 ===== START BOOKING SUBMISSION =====');
    console.log('📅 Submission time:', new Date().toISOString());
    
    // ============================================================
    // STEP 1: CHECK ALL FORM ELEMENTS EXIST
    // ============================================================
    const elements = {
        clientName: document.getElementById('clientName'),
        clientPhone: document.getElementById('clientPhone'),
        serviceId: document.getElementById('serviceId'),
        appointmentDate: document.getElementById('appointmentDate'),
        appointmentTime: document.getElementById('appointmentTime'),
        notes: document.getElementById('notes'),
        form: document.getElementById('bookingForm'),
        submitBtn: document.getElementById('bookingSubmit'),
        errorDiv: document.getElementById('bookingError'),
        successDiv: document.getElementById('bookingSuccess')
    };
    
    console.log('📋 Form elements found:');
    Object.keys(elements).forEach(key => {
        const exists = !!elements[key];
        console.log(`  ${key}: ${exists ? '✅ Found' : '❌ NOT FOUND'}`);
        if (exists && key !== 'form' && key !== 'submitBtn' && key !== 'errorDiv' && key !== 'successDiv') {
            console.log(`    value: "${elements[key].value}"`);
            console.log(`    type: ${typeof elements[key].value}`);
            console.log(`    length: ${elements[key].value?.length || 0}`);
        }
    });
    
    // ============================================================
    // STEP 2: GET RAW VALUES
    // ============================================================
    const rawData = {
        client_name: elements.clientName?.value,
        client_phone: elements.clientPhone?.value,
        service_id: elements.serviceId?.value,
        appointment_date: elements.appointmentDate?.value,
        appointment_time: elements.appointmentTime?.value,
        notes: elements.notes?.value
    };
    
    console.log('📝 RAW form values:');
    Object.keys(rawData).forEach(key => {
        const value = rawData[key];
        const displayValue = value === undefined ? 'undefined' : value === null ? 'null' : `"${value}"`;
        console.log(`  ${key}: ${displayValue}`);
        console.log(`    type: ${typeof value}`);
        console.log(`    length: ${value?.length || 0}`);
        console.log(`    is empty: ${!value || String(value).trim() === ''}`);
    });
    
    // ============================================================
    // STEP 3: CHECK FOR EMPTY/NULL/UNDEFINED VALUES
    // ============================================================
    const requiredFields = [
        'client_name',
        'client_phone',
        'service_id',
        'appointment_date',
        'appointment_time'
    ];
    
    const missingFields = [];
    const emptyFields = [];
    const fieldValues = {};
    
    requiredFields.forEach(field => {
        const value = rawData[field];
        fieldValues[field] = value;
        
        if (value === null || value === undefined) {
            missingFields.push(field);
            console.log(`❌ ${field}: MISSING (null/undefined)`);
        } else if (String(value).trim() === '') {
            emptyFields.push(field);
            console.log(`❌ ${field}: EMPTY (empty string)`);
        } else {
            console.log(`✅ ${field}: VALID = "${String(value).trim()}"`);
        }
    });
    
    console.log('🔍 Validation summary:');
    console.log(`  Missing (null/undefined): ${missingFields.length > 0 ? missingFields.join(', ') : 'None ✅'}`);
    console.log(`  Empty (empty string): ${emptyFields.length > 0 ? emptyFields.join(', ') : 'None ✅'}`);
    console.log(`  All fields valid: ${missingFields.length === 0 && emptyFields.length === 0}`);
    
    // ============================================================
    // STEP 4: CHECK EACH FIELD INDIVIDUALLY
    // ============================================================
    console.log('🔎 Individual field validation:');
    
    // Client Name
    const clientName = rawData.client_name;
    if (!clientName || String(clientName).trim() === '') {
        console.error('❌❌❌ client_name is EMPTY or MISSING');
        console.error('  Value:', clientName);
        console.error('  Type:', typeof clientName);
        showError('Please enter your full name.');
        elements.clientName?.focus();
        return;
    }
    console.log('✅ client_name: PASSED');
    
    // Client Phone
    const clientPhone = rawData.client_phone;
    if (!clientPhone || String(clientPhone).trim() === '') {
        console.error('❌❌❌ client_phone is EMPTY or MISSING');
        console.error('  Value:', clientPhone);
        console.error('  Type:', typeof clientPhone);
        showError('Please enter your phone number.');
        elements.clientPhone?.focus();
        return;
    }
    console.log('✅ client_phone: PASSED');
    
    // Service ID - Check with more detail
    const serviceId = rawData.service_id;
    if (!serviceId || String(serviceId).trim() === '') {
        console.error('❌❌❌ service_id is EMPTY or MISSING');
        console.error('  Value:', serviceId);
        console.error('  Type:', typeof serviceId);
        console.error('  This is likely why the backend is rejecting the request!');
        console.error('  💡 TIP: Make sure your "Book Now" buttons have: onclick="openBookingModal(\'{{ service.id }}\')"');
        console.error('  💡 TIP: Check that {{ service.id }} is being rendered properly in your template');
        showError('No service selected. Please go back and select a service.');
        return;
    }
    console.log('✅ service_id: PASSED');
    
    // Appointment Date
    const appointmentDate = rawData.appointment_date;
    if (!appointmentDate || String(appointmentDate).trim() === '') {
        console.error('❌❌❌ appointment_date is EMPTY or MISSING');
        console.error('  Value:', appointmentDate);
        console.error('  Type:', typeof appointmentDate);
        showError('Please select a date.');
        elements.appointmentDate?.focus();
        return;
    }
    console.log('✅ appointment_date: PASSED');
    
    // Appointment Time
    const appointmentTime = rawData.appointment_time;
    if (!appointmentTime || String(appointmentTime).trim() === '') {
        console.error('❌❌❌ appointment_time is EMPTY or MISSING');
        console.error('  Value:', appointmentTime);
        console.error('  Type:', typeof appointmentTime);
        showError('Please select a time.');
        elements.appointmentTime?.focus();
        return;
    }
    console.log('✅ appointment_time: PASSED');
    
    console.log('✅ ALL REQUIRED FIELDS VALIDATED SUCCESSFULLY!');
    
    // ============================================================
    // STEP 5: PREPARE FINAL DATA
    // ============================================================
    const bookingData = {
        client_name: String(clientName).trim(),
        client_phone: String(clientPhone).trim(),
        service_id: String(serviceId).trim(),
        appointment_date: String(appointmentDate).trim(),
        appointment_time: String(appointmentTime).trim(),
        notes: rawData.notes ? String(rawData.notes).trim() : ''
    };
    
    console.log('📦 FINAL DATA being sent to server:');
    console.log(JSON.stringify(bookingData, null, 2));
    console.log('📦 Data type check:');
    Object.keys(bookingData).forEach(key => {
        const value = bookingData[key];
        console.log(`  ${key}: type=${typeof value}, value="${value}", length=${value.length}`);
    });
    
    // ============================================================
    // STEP 6: SEND TO SERVER
    // ============================================================
    console.log('📤 Sending POST request to /api/book...');
    console.log('📤 Request payload:', JSON.stringify(bookingData));
    
    // Show loading state
    const submitBtn = elements.submitBtn;
    const originalText = submitBtn?.innerHTML || 'Confirm Booking';
    if (submitBtn) {
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        submitBtn.disabled = true;
        console.log('⏳ Loading state activated');
    }
    
    // Hide previous messages
    if (elements.errorDiv) elements.errorDiv.classList.add('hidden');
    if (elements.successDiv) elements.successDiv.classList.add('hidden');
    
    try {
        console.log('⏳ Awaiting server response...');
        const response = await fetch('/api/book', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(bookingData)
        });
        
        console.log('📥 Response received!');
        console.log('📥 Response status:', response.status, response.statusText);
        console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
        
        // Get response as text first for debugging
        const responseText = await response.text();
        console.log('📥 Raw response body:', responseText);
        console.log('📥 Response body length:', responseText.length);
        
        if (!responseText || responseText.trim() === '') {
            console.error('❌ Empty response received!');
            showError('Server returned empty response. Please try again.');
            return;
        }
        
        let result;
        try {
            result = JSON.parse(responseText);
            console.log('📥 Parsed JSON response:', result);
        } catch (parseError) {
            console.error('❌ JSON Parse Error:', parseError);
            console.error('❌ Response that failed to parse:', responseText.substring(0, 200) + '...');
            showError('Server returned invalid response format. Please try again.');
            return;
        }
        
        // ============================================================
        // STEP 7: PROCESS RESPONSE
        // ============================================================
        console.log('🔍 Response analysis:');
        console.log('  success:', result.success);
        console.log('  message:', result.message);
        console.log('  error:', result.error);
        console.log('  missing fields:', result.missing || 'None');
        console.log('  booking_id:', result.booking_id || 'None');
        console.log('  Full result:', result);
        
        if (result.success) {
            console.log('🎉 ✅ BOOKING SUCCESSFUL!');
            console.log('  Booking ID:', result.booking_id);
            console.log('  Message:', result.message);
            
            if (elements.successDiv) {
                elements.successDiv.textContent = '✅ ' + (result.message || 'Booking confirmed! We will contact you shortly.');
                elements.successDiv.classList.remove('hidden');
                console.log('✅ Success message displayed');
            }
            
            if (result.whatsapp_url) {
                console.log('📱 WhatsApp URL generated:', result.whatsapp_url);
                setTimeout(() => {
                    console.log('📱 Opening WhatsApp...');
                    window.open(result.whatsapp_url, '_blank');
                }, 500);
            }
            
            console.log('⏳ Closing modal in 3 seconds...');
            setTimeout(() => {
                closeBookingModal();
                const form = document.getElementById('bookingForm');
                if (form) {
                    form.reset();
                    console.log('✅ Form reset after successful booking');
                }
            }, 3000);
        } else {
            console.error('❌ ❌ ❌ BOOKING FAILED!');
            console.error('  Error message:', result.error);
            console.error('  Missing fields:', result.missing || 'None specified');
            console.error('  Debug info:', result.debug || 'None');
            
            let errorMessage = result.error || 'Booking failed. Please try again.';
            if (result.missing && result.missing.length > 0) {
                errorMessage = `Missing required fields: ${result.missing.join(', ')}`;
                console.error('❌ Missing fields from server:', result.missing);
            }
            
            if (result.debug) {
                console.error('❌ Server debug info:', result.debug);
            }
            
            showError(errorMessage);
        }
    } catch (error) {
        console.error('❌ 💥 NETWORK/REQUEST ERROR:', error);
        console.error('❌ Error name:', error.name);
        console.error('❌ Error message:', error.message);
        console.error('❌ Error stack:', error.stack);
        
        let errorMessage = 'Network error. ';
        if (error.message) {
            errorMessage += error.message;
        } else {
            errorMessage += 'Please check your connection and try again.';
        }
        showError(errorMessage);
    } finally {
        if (submitBtn) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            console.log('✅ Submit button restored');
        }
    }
    
    console.log('🏁 ===== END BOOKING SUBMISSION =====');
    console.log('📅 End time:', new Date().toISOString());
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    console.log('⚠️ showError called with message:', message);
    
    const errorDiv = document.getElementById('bookingError');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
        console.log('✅ Error message displayed:', message);
    } else {
        console.error('❌ Error div not found!');
        alert(message);
    }
    
    const successDiv = document.getElementById('bookingSuccess');
    if (successDiv) {
        successDiv.classList.add('hidden');
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv) {
            errorDiv.classList.add('hidden');
            console.log('⚠️ Error message auto-hidden after 5 seconds');
        }
    }, 5000);
}

// ============================================================
// NAVBAR TOGGLE (Mobile)
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM Content Loaded');
    console.log('📍 Current path:', window.location.pathname);
    
    // Mobile menu toggle
    const menuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (menuBtn && mobileMenu) {
        console.log('✅ Mobile menu elements found');
        menuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
            console.log('📱 Mobile menu toggled, hidden:', mobileMenu.classList.contains('hidden'));
        });
    } else {
        console.warn('⚠️ Mobile menu elements not found');
        if (!menuBtn) console.warn('  mobileMenuBtn not found');
        if (!mobileMenu) console.warn('  mobileMenu not found');
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
            console.log('⌨️ ESC key pressed, closing modal');
            closeBookingModal();
        }
    });
    
    // Click outside modal to close
    const modalOverlay = document.querySelector('.modal-overlay');
    if (modalOverlay) {
        console.log('✅ Modal overlay found');
        modalOverlay.addEventListener('click', function() {
            console.log('🖱️ Clicked outside modal, closing');
            closeBookingModal();
        });
    } else {
        console.warn('⚠️ Modal overlay not found');
    }
    
    // Set min date for appointment date picker
    const dateInput = document.getElementById('appointmentDate');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.min = tomorrow.toISOString().split('T')[0];
        console.log('📅 Set min date for date picker to:', dateInput.min);
    } else {
        console.warn('⚠️ appointmentDate input not found');
    }
    
    // Check if service cards exist
    const serviceCards = document.querySelectorAll('[onclick*="openBookingModal"]');
    console.log('📋 Service cards with openBookingModal:', serviceCards.length);
    if (serviceCards.length > 0) {
        console.log('✅ Found service cards with booking functionality');
        // Log the onclick attributes to see what's being passed
        serviceCards.forEach((card, index) => {
            const onclick = card.getAttribute('onclick');
            console.log(`  Card ${index + 1}: onclick="${onclick}"`);
        });
    } else {
        console.warn('⚠️ No service cards with openBookingModal found');
    }
    
    // Check if booking modal exists
    const modal = document.getElementById('bookingModal');
    if (modal) {
        console.log('✅ Booking modal found in DOM');
    } else {
        console.warn('⚠️ Booking modal NOT found in DOM');
    }
    
    console.log('✅ Main.js initialization complete');
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
                console.log('📜 Smooth scrolling to:', targetId);
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
    console.log('🖼️ Lazy loading images found:', lazyImages.length);
    
    const imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src || img.src;
                img.classList.remove('opacity-0');
                imageObserver.unobserve(img);
                console.log('🖼️ Image loaded:', img.src);
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
    console.log('✅ Contact form found');
    contactForm.addEventListener('submit', async function(event) {
        event.preventDefault();
        console.log('📝 Contact form submitted');
        
        const formData = new FormData(this);
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value.trim();
        });
        console.log('📤 Contact form data:', data);
        
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
            console.log('📥 Contact form response:', result);
            
            if (result.success) {
                alert('✅ Message sent successfully! We will get back to you soon.');
                this.reset();
            } else {
                alert('❌ Error: ' + (result.error || 'Failed to send message.'));
            }
        } catch (error) {
            console.error('❌ Contact form error:', error);
            alert('❌ Network error. Please try again.');
        } finally {
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        }
    });
} else {
    console.log('ℹ️ Contact form not found (optional)');
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
// EXPOSE FUNCTIONS GLOBALLY
// ============================================================

// Make functions available globally for inline onclick handlers
window.openBookingModal = openBookingModal;
window.closeBookingModal = closeBookingModal;
window.handleBookingSubmit = handleBookingSubmit;
window.showError = showError;
window.formatCurrency = formatCurrency;

console.log('✅ All functions exposed globally');
console.log('📋 Available functions:');
console.log('  - openBookingModal(serviceId)');
console.log('  - closeBookingModal()');
console.log('  - handleBookingSubmit(event)');
console.log('  - showError(message)');
console.log('  - formatCurrency(amount)');
console.log('  - getTodayDate()');
console.log('  - getTomorrowDate()');

console.log('🚀 ===== MAIN.JS LOADED SUCCESSFULLY =====');