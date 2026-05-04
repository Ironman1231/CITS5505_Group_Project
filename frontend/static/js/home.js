let map = L.map('map', {
  scrollWheelZoom: false
}).setView([-31.9805, 115.8178], 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

markerData.forEach(function(m) {
  L.marker([m.lat, m.lng])
    .addTo(map)
    .bindPopup("<strong>" + m.title + "</strong><br>" + m.category);
});
