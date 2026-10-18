/**
 * RoadPulse Map Controller
 * Loads hazards from Flask backend /api/reports, renders color-coded risk markers,
 * handles filter changes, and shows detailed popups.
 */

document.addEventListener('DOMContentLoaded', function() {
  const mapElement = document.getElementById('map');
  if (!mapElement) return;

  // Initial center around Hyderabad, India per specification
  const initialLat = 17.4435;
  const initialLng = 78.3772;
  const initialZoom = 12;

  const map = L.map('map').setView([initialLat, initialLng], initialZoom);

  // Free OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  let markersLayer = L.layerGroup().addTo(map);

  const categoryFilter = document.getElementById('filter-category');
  const severityFilter = document.getElementById('filter-severity');
  const statusFilter = document.getElementById('filter-status');
  const resetBtn = document.getElementById('btn-reset-filters');
  const emptyResetBtn = document.getElementById('btn-empty-reset');
  const countLabel = document.getElementById('reports-count-label');
  const emptyState = document.getElementById('map-empty-state');

  // Custom colored divIcon maker based on risk classification
  function createCustomMarker(riskClassification) {
    const cls = (riskClassification || 'low').toLowerCase();
    return L.divIcon({
      className: 'custom-leaflet-marker',
      html: `<div class="custom-pin pin-${cls}"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 24],
      popupAnchor: [0, -22]
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
        if (response.status !== 'success') {
          console.error("API response error:", response);
          return;
        }

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
          const sampleLabel = report.is_sample ? `<span style="font-size: 0.7rem; background:#f1f5f9; padding:2px 5px; border-radius:3px; color:#64748b;">Sample</span>` : '';

          const popupContent = `
            <div style="min-width: 220px; font-family: inherit;">
              <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:0.5rem; margin-bottom: 0.35rem;">
                <span class="badge ${badgeClass}" style="font-size:0.7rem;">${report.risk_classification} Risk (${report.road_risk_score}/100)</span>
                ${sampleLabel}
              </div>
              <h4 style="font-size: 0.95rem; font-weight:700; margin-bottom: 0.25rem; color: #0f172a;">${report.title}</h4>
              <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.4rem;">
                <strong>Category:</strong> ${report.category} | <strong>Severity:</strong> ${report.severity}
              </div>
              <div style="font-size: 0.8rem; color: #64748b; margin-bottom: 0.6rem;">
                📍 ${report.location_name}
              </div>
              <div style="font-size: 0.78rem; background: #f8fafc; padding: 0.4rem; border-radius: 4px; margin-bottom: 0.6rem; border: 1px solid #e2e8f0;">
                <em>"${report.risk_explanation || 'Experimental prioritization score.'}"</em>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size: 0.75rem; color: #94a3b8;">Status: <strong>${report.status}</strong></span>
                <a href="/report/${report.id}" style="color: #2563eb; font-size: 0.8rem; font-weight:600; text-decoration:none;">Details →</a>
              </div>
            </div>
          `;

          marker.bindPopup(popupContent);
          markersLayer.addLayer(marker);
        });

        // Fit map bounds if markers exist
        if (latLngBounds.length > 0) {
          map.fitBounds(latLngBounds, { padding: [40, 40], maxZoom: 14 });
        }
      })
      .catch(err => {
        console.error("Error fetching map reports:", err);
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

  // Initial load
  fetchAndRenderReports();
});
