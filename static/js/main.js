/**
 * Main application JavaScript utilities
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile sidebar toggle handler
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');

  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('show');
    });

    // Close sidebar on click outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth < 992 && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && e.target !== sidebarToggle) {
          sidebar.classList.remove('show');
        }
      }
    });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach((alert) => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });
});
