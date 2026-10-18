/**
 * RoadPulse Gen-Z Dark Mode Chart.js Analytics Controller
 * Renders glowing neon charts calibrated for OLED dark backgrounds.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Global Chart.js dark mode defaults
  Chart.defaults.color = '#94a3b8';
  Chart.defaults.font.family = "'Plus Jakarta Sans', sans-serif";
  Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.08)';

  fetch('/api/analytics')
    .then(res => res.json())
    .then(response => {
      if (response.status !== 'success') return;
      const data = response.data;

      // 1. Categories Chart (Gen-Z Neon Doughnut)
      const catCtx = document.getElementById('chart-categories');
      if (catCtx) {
        const catLabels = data.categories.map(c => c.category);
        const catCounts = data.categories.map(c => c.count);
        new Chart(catCtx, {
          type: 'doughnut',
          data: {
            labels: catLabels,
            datasets: [{
              data: catCounts,
              backgroundColor: [
                '#6366f1', // Electric Indigo
                '#06b6d4', // Cyber Cyan
                '#facc15', // Laser Gold
                '#ff3366', // Neon Crimson
                '#10b981', // Neon Emerald
                '#a855f7'  // Neon Purple
              ],
              borderWidth: 2,
              borderColor: '#0f172a',
              hoverOffset: 6
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
                  padding: 15,
                  font: { size: 11, weight: '600' },
                  color: '#cbd5e1'
                }
              }
            }
          }
        });
      }

      // 2. Severity Chart (Neon Vertical Bars)
      const sevCtx = document.getElementById('chart-severities');
      if (sevCtx) {
        const sevOrder = ['Low', 'Medium', 'High', 'Critical'];
        const sevColors = {
          'Low': '#10b981',
          'Medium': '#facc15',
          'High': '#ff8c00',
          'Critical': '#ff3366'
        };

        const sevMap = {};
        data.severities.forEach(s => {
          sevMap[s.severity] = s.count;
        });

        new Chart(sevCtx, {
          type: 'bar',
          data: {
            labels: sevOrder,
            datasets: [{
              label: 'Report Count',
              data: sevOrder.map(sev => sevMap[sev] || 0),
              backgroundColor: sevOrder.map(sev => sevColors[sev]),
              borderRadius: 8,
              borderWidth: 1,
              borderColor: sevOrder.map(sev => sevColors[sev])
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              x: {
                grid: { display: false },
                ticks: { color: '#94a3b8', font: { weight: '600' } }
              },
              y: {
                beginAtZero: true,
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { precision: 0, color: '#94a3b8' }
              }
            }
          }
        });
      }

      // 3. Risk Distribution Chart
      const riskCtx = document.getElementById('chart-risk-dist');
      if (riskCtx) {
        const riskLevels = ['Low', 'Medium', 'High', 'Critical'];
        const riskColors = ['#10b981', '#facc15', '#ff8c00', '#ff3366'];
        const riskMap = {};
        data.risk_distribution.forEach(r => {
          riskMap[r.risk_classification] = r.count;
        });

        new Chart(riskCtx, {
          type: 'bar',
          data: {
            labels: ['Low (0-24)', 'Medium (25-49)', 'High (50-74)', 'Critical (75-100)'],
            datasets: [{
              label: 'Incidents in Range',
              data: riskLevels.map(lvl => riskMap[lvl] || 0),
              backgroundColor: riskColors,
              borderRadius: 8,
              borderWidth: 1,
              borderColor: riskColors
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              x: {
                grid: { display: false },
                ticks: { color: '#94a3b8', font: { weight: '600' } }
              },
              y: {
                beginAtZero: true,
                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                ticks: { precision: 0, color: '#94a3b8' }
              }
            }
          }
        });
      }

      // 4. Status Breakdown Chart
      const statusCtx = document.getElementById('chart-statuses');
      if (statusCtx) {
        const statusLabels = data.statuses.map(s => s.status);
        const statusCounts = data.statuses.map(s => s.count);
        new Chart(statusCtx, {
          type: 'pie',
          data: {
            labels: statusLabels,
            datasets: [{
              data: statusCounts,
              backgroundColor: ['#64748b', '#38bdf8', '#facc15', '#10b981'],
              borderWidth: 2,
              borderColor: '#0f172a'
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
                  padding: 15,
                  font: { size: 11, weight: '600' },
                  color: '#cbd5e1'
                }
              }
            }
          }
        });
      }
    })
    .catch(err => {
      console.error("Failed to render Chart.js analytics:", err);
      const chartsContainer = document.querySelector('.charts-grid');
      if (chartsContainer) {
        const errorNotice = document.createElement('div');
        errorNotice.className = 'flash-alert flash-error';
        errorNotice.style.gridColumn = '1 / -1';
        errorNotice.innerHTML = '<span>⚠️ Unable to load live analytics charts. Please verify network connection or reload.</span>';
        chartsContainer.prepend(errorNotice);
      }
    });
});

