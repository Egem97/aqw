/**
 * APG PACKING - Corporate JavaScript
 * Enhanced functionality for the corporate management system
 */

// Global APG namespace
window.APG = window.APG || {};

// Corporate utilities
APG.Utils = {
    // Format currency
    formatCurrency: (amount, currency = 'PEN') => {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        }).format(amount);
    },

    // Format date
    formatDate: (date, options = {}) => {
        const defaultOptions = {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        };
        return new Date(date).toLocaleDateString('es-PE', { ...defaultOptions, ...options });
    },

    // Format numbers
    formatNumber: (number, decimals = 2) => {
        return new Intl.NumberFormat('es-PE', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(number);
    },

    // Show loading overlay
    showLoading: () => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.remove('hidden');
            overlay.classList.add('flex');
        }
    },

    // Hide loading overlay
    hideLoading: () => {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.classList.add('hidden');
            overlay.classList.remove('flex');
        }
    },

    // Show toast notification
    showToast: (message, type = 'info', duration = 5000) => {
        const toast = document.createElement('div');
        const icons = {
            success: 'fas fa-check-circle text-green-500',
            error: 'fas fa-exclamation-circle text-red-500',
            warning: 'fas fa-exclamation-triangle text-yellow-500',
            info: 'fas fa-info-circle text-blue-500'
        };

        toast.className = `
            fixed top-20 right-4 z-50 max-w-sm w-full bg-white shadow-lg rounded-lg 
            pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden
            transform transition-all duration-300 ease-in-out translate-x-full opacity-0
        `;

        toast.innerHTML = `
            <div class="p-4">
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i class="${icons[type] || icons.info}"></i>
                    </div>
                    <div class="ml-3 w-0 flex-1 pt-0.5">
                        <p class="text-sm font-medium text-gray-900">${message}</p>
                    </div>
                    <div class="ml-4 flex-shrink-0 flex">
                        <button onclick="this.closest('.fixed').remove()" 
                                class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-600">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full', 'opacity-0');
        }, 100);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('translate-x-full', 'opacity-0');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    },

    // Debounce function
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Copy to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            APG.Utils.showToast('Copiado al portapapeles', 'success');
        } catch (err) {
            console.error('Error copying to clipboard:', err);
            APG.Utils.showToast('Error al copiar', 'error');
        }
    }
};

// Image handling utilities
APG.Images = {
    // Lazy load images
    lazyLoad: () => {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('opacity-0');
                    img.classList.add('opacity-100');
                    observer.unobserve(img);
                }
            });
        });

        images.forEach(img => imageObserver.observe(img));
    },

    // Handle image errors
    handleError: (img, fallbackSrc = '/static/images/placeholder.png') => {
        img.onerror = () => {
            img.src = fallbackSrc;
            img.classList.add('opacity-75');
        };
    },

    // Preload critical images
    preload: (urls) => {
        urls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = url;
            document.head.appendChild(link);
        });
    }
};

// API utilities
APG.API = {
    // Base fetch with error handling
    fetch: async (url, options = {}) => {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': APG.Utils.getCSRFToken(),
                ...options.headers
            },
            credentials: 'same-origin',
            ...options
        };

        try {
            APG.Utils.showLoading();
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API Error:', error);
            APG.Utils.showToast('Error en la conexión', 'error');
            throw error;
        } finally {
            APG.Utils.hideLoading();
        }
    },

    // Get CSRF token
    getCSRFToken: () => {
        const token = document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                     document.querySelector('meta[name="csrf-token"]')?.content ||
                     window.csrfToken;
        return token;
    }
};

// Dashboard utilities
APG.Dashboard = {
    // Update stats in real-time
    updateStats: async () => {
        try {
            const response = await APG.API.fetch('/management/api/dashboard-stats/');
            if (response.success) {
                APG.Dashboard.renderStats(response.data);
            }
        } catch (error) {
            console.error('Error updating stats:', error);
        }
    },

    // Render updated stats
    renderStats: (data) => {
        Object.keys(data).forEach(key => {
            const element = document.querySelector(`[data-stat="${key}"]`);
            if (element) {
                if (key === 'monthly_costs') {
                    element.textContent = APG.Utils.formatCurrency(data[key]);
                } else {
                    element.textContent = APG.Utils.formatNumber(data[key], 0);
                }
            }
        });
    },

    // Auto-refresh dashboard
    startAutoRefresh: (interval = 30000) => {
        setInterval(APG.Dashboard.updateStats, interval);
    }
};

// Form utilities
APG.Forms = {
    // Enhanced form validation
    validate: (form) => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value.trim()) {
                APG.Forms.showFieldError(input, 'Este campo es requerido');
                isValid = false;
            } else {
                APG.Forms.clearFieldError(input);
            }
        });

        return isValid;
    },

    // Show field error
    showFieldError: (field, message) => {
        field.classList.add('border-red-500');
        const errorDiv = field.parentNode.querySelector('.field-error') || document.createElement('div');
        errorDiv.className = 'field-error text-red-500 text-sm mt-1';
        errorDiv.textContent = message;
        if (!field.parentNode.querySelector('.field-error')) {
            field.parentNode.appendChild(errorDiv);
        }
    },

    // Clear field error
    clearFieldError: (field) => {
        field.classList.remove('border-red-500');
        const errorDiv = field.parentNode.querySelector('.field-error');
        if (errorDiv) {
            errorDiv.remove();
        }
    },

    // Auto-save form data
    autoSave: (form, key) => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        localStorage.setItem(`apg_form_${key}`, JSON.stringify(data));
    },

    // Restore form data
    restore: (form, key) => {
        const saved = localStorage.getItem(`apg_form_${key}`);
        if (saved) {
            const data = JSON.parse(saved);
            Object.keys(data).forEach(name => {
                const field = form.querySelector(`[name="${name}"]`);
                if (field) {
                    field.value = data[name];
                }
            });
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize lazy loading
    APG.Images.lazyLoad();

    // Add image error handling
    document.querySelectorAll('img').forEach(img => {
        APG.Images.handleError(img);
    });

    // Initialize auto-refresh on dashboard
    if (document.querySelector('[data-page="dashboard"]')) {
        APG.Dashboard.startAutoRefresh();
    }

    // Add form validation to all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', (e) => {
            if (!APG.Forms.validate(form)) {
                e.preventDefault();
                APG.Utils.showToast('Por favor completa todos los campos requeridos', 'warning');
            }
        });
    });

    // Add auto-save to forms with data-autosave
    document.querySelectorAll('form[data-autosave]').forEach(form => {
        const key = form.dataset.autosave;
        APG.Forms.restore(form, key);
        
        form.addEventListener('input', APG.Utils.debounce(() => {
            APG.Forms.autoSave(form, key);
        }, 1000));
    });

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const target = document.querySelector(link.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    console.log('🚀 APG PACKING Corporate System initialized');
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APG;
}
