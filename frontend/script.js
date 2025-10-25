// Simple navigation functionality for home page
document.addEventListener('DOMContentLoaded', function() {
    // Set active class for home link
    const homeLink = document.querySelector('.nav-link[href="home.html"]');
    if (homeLink) {
        homeLink.classList.add('active');
    }

    // Handle navigation to record page
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === 'record.html') {
                // Allow default link behavior for external pages
            } else if (href === 'home.html') {
                // Prevent default for home link if already on home page
                e.preventDefault();
            }
        });
    });

    const startRecordingBtn = document.querySelector('.btn-primary');
    if (startRecordingBtn) {
        startRecordingBtn.addEventListener('click', function(e) {
            // Allow default link behavior to record.html
        });
    }
});
