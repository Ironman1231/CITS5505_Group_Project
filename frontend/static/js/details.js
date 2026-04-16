var mapCenter = [-31.9789, 115.8148];

var map = L.map('place-map').setView(mapCenter, 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

L.marker(mapCenter)
    .addTo(map)
    .bindPopup('Matilda Bay')
    .openPopup();
