/**
 * RoadPulse Gen-Z Dark Mode Leaflet Map Controller
 * Renders glowing custom pins, sleek dark popups, and handles interactive filters.
 */

document.addEventListener('DOMContentLoaded', function() {
  const mapElement = document.getElementById('map');
  if (!mapElement) return;

  const initialLat = 17.4435;
  const initialLng = 78.3772;
  const initialZoom = 12;

  const map = L.map('map').setView([initialLat, initialLng], initialZoom);

  // Free OpenStreetMap tile layer (styled to dark cyber theme via CSS filter)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright" style="color:#38bdf8;">OpenStreetMap</a> contributors'
  }).addTo(map);

  let markersLayer = L.layerGroup().addTo(map);

  const categoryFilter = document.getElementById('filter-category');
  const severityFilter = document.getElementById('filter-severity');
  const statusFilter = document.getElementById('filter-status');
  const resetBtn = document.getElementById('btn-reset-filters');
  const emptyResetBtn = document.getElementById('btn-empty-reset');
  const countLabel = document.getElementById('reports-count-label');
  const emptyState = document.getElementById('map-empty-state');

  // Custom glowing neon pin
  function createCustomMarker(riskClassification) {
    const cls = (riskClassification || 'low').toLowerCase();
    return L.divIcon({
      className: 'custom-leaflet-marker',
      html: `<div class="custom-pin pin-${cls}"></div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 26],
      popupAnchor: [0, -24]
    });
  }

  function fetchAndRenderReports() {
    const params = new URLSearchParams();
    if (categoryFilter.value) params.append('category', categoryFilter.value);
    if (severityFilter.value) params.append('severity', severityFilter.value);
    if (statusFilter.value) params.append('status', statusFilter.value);

    fetch(`/api/reports?${params.toString()}`)
      .then(res => res.json())
      .then(response => {
        if (response.status !== 'success') return;

        markersLayer.clearLayers();
        const reports = response.data;
        countLabel.textContent = reports.length;

        if (reports.length === 0) {
          emptyState.style.display = 'block';
          return;
        } else {
          emptyState.style.display = 'none';
        }

        const latLngBounds = [];

        reports.forEach(report => {
          const lat = parseFloat(report.latitude);
          const lng = parseFloat(report.longitude);
          latLngBounds.push([lat, lng]);

          const markerIcon = createCustomMarker(report.risk_classification);
          const marker = L.marker([lat, lng], { icon: markerIcon });

          const badgeClass = `badge-${(report.risk_classification || 'low').toLowerCase()}`;
          const sampleLabel = report.is_sample ? `<span style="font-size:0.68rem; background:rgba(255,255,255,0.06); padding:2px 6px; border-radius:4px; color:#94a3b8; border:1px solid rgba(255,255,255,0.08);">Sample</span>` : '';

          const popupContent = `
            <div style="min-width: 230px; font-family: 'Plus Jakarta Sans', sans-serif;">
              <div style="display:flex; justify-content:space-between; align-items:center; gap:0.5rem; margin-bottom: 0.5rem;">
                <span class="badge ${badgeClass}" style="font-size:0.7rem;">${report.risk_classification} Priority (${report.road_risk_score}/100)</span>
                ${sampleLabel}
              </div>
              <h4 style="font-size: 1rem; font-weight:800; margin-bottom: 0.35rem; color: #ffffff;">${report.title}</h4>
              <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.45rem;">
                <strong>Category:</strong> <span style="color:#38bdf8;">${report.category}</span> | <strong>Severity:</strong> ${report.severity}
              </div>
              <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.65rem;">
                📍 ${report.location_name}
              </div>
              <div style="font-size: 0.78rem; background: rgba(0,0,0,0.3); padding: 0.5rem 0.65rem; border-radius: 8px; margin-bottom: 0.75rem; border: 1px solid rgba(255,255,255,0.06); color: #cbd5e1;">
                <em>"${report.risk_explanation || 'Experimental prioritization score.'}"</em>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.08); padding-top:0.5rem;">
                <span style="font-size: 0.75rem; color: #64748b;">Status: <strong style="color:#e2e8f0;">${report.status}</strong></span>
                <a href="/report/${report.id}" style="color: #38bdf8; font-size: 0.82rem; font-weight:700; text-decoration:none;">View Intel →</a>
              </div>
            </div>
          `;

          marker.bindPopup(popupContent);
          markersLayer.addLayer(marker);
        });

        if (latLngBounds.length > 0) {
          map.fitBounds(latLngBounds, { padding: [40, 40], maxZoom: 14 });
        }
      })
      .catch(err => {
        console.error("Error fetching map reports:", err);
        countLabel.textContent = "Offline / Error";
        emptyState.style.display = 'block';
        emptyState.innerHTML = `
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚠️</div>
          <h3 style="font-size: 1.15rem; color: #ffffff; margin-bottom: 0.35rem; font-weight: 700;">Connection Error</h3>
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1.25rem;">
            Failed to retrieve live hazard signals from backend.
          </p>
          <button onclick="location.reload()" class="btn btn-primary btn-sm">Reload Map</button>
        `;
      });
  }


  // Filter Event Listeners
  categoryFilter.addEventListener('change', fetchAndRenderReports);
  severityFilter.addEventListener('change', fetchAndRenderReports);
  statusFilter.addEventListener('change', fetchAndRenderReports);

  function resetAllFilters() {
    categoryFilter.value = '';
    severityFilter.value = '';
    statusFilter.value = '';
    fetchAndRenderReports();
  }

  resetBtn.addEventListener('click', resetAllFilters);
  if (emptyResetBtn) emptyResetBtn.addEventListener('click', resetAllFilters);

  fetchAndRenderReports();
});
