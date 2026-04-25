let map = L.map('map').setView([-31.9805, 115.8178], 14);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

let markers = [
  { name: 'Matilda Bay',        lat: -31.9789, lng: 115.8148 },
  { name: 'Reid Library',       lat: -31.9800, lng: 115.8183 },
  { name: 'UWA Oak Lawn',       lat: -31.9795, lng: 115.8170 },
  { name: 'Kings Park',         lat: -31.9614, lng: 115.8310 },
  { name: 'Chicho Gelato',      lat: -31.9415, lng: 115.8733 },
  { name: 'Fremantle Markets',  lat: -32.0554, lng: 115.7508 },
  { name: 'Elizabeth Quay',     lat: -31.9586, lng: 115.8597 },
  { name: 'Northbridge',        lat: -31.9468, lng: 115.8585 }
];

for (let i = 0; i < markers.length; i++) {
  L.marker([markers[i].lat, markers[i].lng])
    .addTo(map)
    .bindPopup(markers[i].name);
}