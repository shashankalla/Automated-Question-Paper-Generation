/**
 * Automated Question Paper Generation System – main.js
 * General-purpose frontend utilities.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss flash messages after 5 seconds
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.4s';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });

    // Confirm before form submits that include data-confirm attribute
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('submit', (e) => {
            if (!confirm(el.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });
});
