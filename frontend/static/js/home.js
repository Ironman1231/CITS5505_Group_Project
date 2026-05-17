let map = L.map('map', {
  scrollWheelZoom: false
}).setView([-31.9805, 115.8178], 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

markerData.forEach(function(m) {
  var popup = document.createElement('div');
  popup.className = 'perthpins-popup';

  var title = document.createElement('strong');
  title.className = 'perthpins-popup-title';
  title.textContent = m.title;

  var category = document.createElement('span');
  category.className = 'perthpins-popup-category';
  category.textContent = m.category;

  popup.appendChild(title);
  popup.appendChild(category);

  L.marker([m.lat, m.lng])
    .addTo(map)
    .bindPopup(popup);
});
