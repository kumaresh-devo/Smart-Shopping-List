/**
 * Expense Reports Chart.js Initialization
 */

document.addEventListener('DOMContentLoaded', () => {
  const greenPalette = [
    '#10b981', '#059669', '#34d399', '#6ee7b7', '#047857',
    '#0f766e', '#14b8a6', '#0d9488', '#64748b', '#94a3b8', '#3b82f6'
  ];

  // 1. Category Breakdown Donut Chart
  const categoryCanvas = document.getElementById('categoryChart');
  if (categoryCanvas && window.REPORT_CATEGORY_DATA && window.REPORT_CATEGORY_DATA.length > 0) {
    const labels = window.REPORT_CATEGORY_DATA.map(item => item.category);
    const data = window.REPORT_CATEGORY_DATA.map(item => item.amount);

    new Chart(categoryCanvas, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: data,
          backgroundColor: greenPalette.slice(0, labels.length),
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              font: { size: 11, family: "'Segoe UI', sans-serif" }
            }
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const val = context.raw || 0;
                return ` ${label}: ₹${val.toFixed(2)}`;
              }
            }
          }
        },
        cutout: '68%'
      }
    });
  }

  // 2. Spending Timeline Bar Chart
  const monthlyCanvas = document.getElementById('monthlyChart');
  if (monthlyCanvas && window.REPORT_MONTHLY_DATA && Object.keys(window.REPORT_MONTHLY_DATA).length > 0) {
    const labels = Object.keys(window.REPORT_MONTHLY_DATA);
    const data = Object.values(window.REPORT_MONTHLY_DATA);

    new Chart(monthlyCanvas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Total Spent (₹)',
          data: data,
          backgroundColor: 'rgba(16, 185, 129, 0.85)',
          hoverBackgroundColor: '#059669',
          borderRadius: 8,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function(value) {
                return '₹' + value;
              }
            },
            grid: {
              color: '#f1f5f9'
            }
          },
          x: {
            grid: {
              display: false
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                return ` Spent: ₹${context.raw.toFixed(2)}`;
              }
            }
          }
        }
      }
    });
  }
});
