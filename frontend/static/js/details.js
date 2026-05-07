var detailData = window.detailMapData || {
    lat: -31.9789,
    lng: 115.8148,
    title: 'Selected check-in',
    category: 'PerthPins'
};
var mapCenter = [detailData.lat, detailData.lng];

var map = L.map('detail-map').setView(mapCenter, 15);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

var popupContent = document.createElement('div');
var popupTitle = document.createElement('strong');
var popupCategory = document.createElement('div');

popupTitle.textContent = detailData.title;
popupCategory.textContent = detailData.category;
popupCategory.className = 'small text-muted';
popupContent.appendChild(popupTitle);
popupContent.appendChild(popupCategory);

L.marker(mapCenter)
    .addTo(map)
    .bindPopup(popupContent)
    .openPopup();
