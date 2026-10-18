/**
 * RoadPulse Chart.js Analytics Controller
 * Fetches JSON metrics from /api/analytics and renders responsive, color-coordinated charts.
 */

document.addEventListener('DOMContentLoaded', function() {
  fetch('/api/analytics')
    .then(res => res.json())
    .then(response => {
      if (response.status !== 'success') return;
      const data = response.data;

      // 1. Categories Chart (Doughnut)
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
              backgroundColor: ['#2563eb', '#38bdf8', '#f59e0b', '#dc2626', '#10b981', '#64748b'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
            }
          }
        });
      }

      // 2. Severity Chart (Bar)
      const sevCtx = document.getElementById('chart-severities');
      if (sevCtx) {
        const sevOrder = ['Low', 'Medium', 'High', 'Critical'];
        const sevColors = {
          'Low': '#16a34a',
          'Medium': '#d97706',
          'High': '#ea580c',
          'Critical': '#dc2626'
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
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, ticks: { precision: 0 } }
            }
          }
        });
      }

      // 3. Risk Distribution Chart (Polar Area or Bar)
      const riskCtx = document.getElementById('chart-risk-dist');
      if (riskCtx) {
        const riskLevels = ['Low', 'Medium', 'High', 'Critical'];
        const riskColors = ['#16a34a', '#d97706', '#ea580c', '#dc2626'];
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
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
              y: { beginAtZero: true, ticks: { precision: 0 } }
            }
          }
        });
      }

      // 4. Status Breakdown Chart (Pie)
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
              backgroundColor: ['#64748b', '#3b82f6', '#f59e0b', '#10b981'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
            }
          }
        });
      }
    })
    .catch(err => {
      console.error("Failed to render Chart.js analytics:", err);
    });
});
