// Initialize the map
var map = L.map('map').setView([51.505, -0.09], 13);
var pickupMarker, receiverMarker;

// Add a tile layer (e.g., OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Define grid parameters
var gridBounds = [
    [40.6, -74.3], // Southwest corner
    [40.9, -73.7]  // Northeast corner
];
var gridSize = 0.1; // Grid cell size in degrees

// Add grid overlay to the map
function addGridOverlay() {
    // Create horizontal grid lines
    for (var lat = gridBounds[0][0]; lat <= gridBounds[1][0]; lat += gridSize) {
        L.polyline([[lat, gridBounds[0][1]], [lat, gridBounds[1][1]]], { color: 'blue', opacity: 0.5 }).addTo(map);
    }

    // Create vertical grid lines
    for (var lng = gridBounds[0][1]; lng <= gridBounds[1][1]; lng += gridSize) {
        L.polyline([[gridBounds[0][0], lng], [gridBounds[1][0], lng]], { color: 'blue', opacity: 0.5 }).addTo(map);
    }
}

// Call function to add grid overlay
addGridOverlay();

// Define marker locations
var markerLocations = [
    { lat: 40.7128, lng: -74.0060, name: 'New York City', description: 'The Big Apple' },
    { lat: 34.0522, lng: -118.2437, name: 'Los Angeles', description: 'City of Angels' },
    { lat: -1.286389, lng: 36.817223, name: 'Nairobi', description: 'Capital City of Kenya' },
    { lat: -4.0435, lng: 39.6682, name: 'Mombasa', description: 'Coastal City in Kenya' }
];
// Function to add or update pickup marker
function addOrUpdatePickupMarker() {
    var pickupLocation = document.getElementById('pickupLocation').value;
    if (pickupMarker) {
        pickupMarker.setLatLng(pickupLocation).update();
    } else {
        pickupMarker = L.marker(pickupLocation).addTo(map);
    }
}

// Function to add or update receiver marker
function addOrUpdateReceiverMarker() {
    var receiverLocation = document.getElementById('deliveryLocation').value;
    if (receiverMarker) {
        receiverMarker.setLatLng(receiverLocation).update();
    } else {
        receiverMarker = L.marker(receiverLocation).addTo(map);
    }
}

// Update markers when the form is submitted
document.getElementById('parcelForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent form submission
    addOrUpdatePickupMarker();
    addOrUpdateReceiverMarker();
});

// Add event listener for pickup location input
document.getElementById('pickupLocation').addEventListener('input', function() {
    var pickupLocation = document.getElementById('pickupLocation').value;
    addOrUpdatePickupMarker(pickupLocation);
});

// Add event listener for receiver location input
document.getElementById('deliveryLocation').addEventListener('input', function() {
    var deliveryLocation = document.getElementById('deliveryLocation').value;
    addOrUpdateReceiverMarker(deliveryLocation);
});

// Add markers to the map
function addMarkers() {
    markerLocations.forEach(function(location) {
        var marker = L.marker([location.lat, location.lng]).addTo(map);

        // Add popup with name and description
        marker.bindPopup('<b>' + location.name + '</b><br>' + location.description);

        // Add tooltip with name
        marker.bindTooltip(location.name);
    });
}

// Function to center the map on the user's location
function centerMapOnUserLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var userLocation = [position.coords.latitude, position.coords.longitude];
            map.setView(userLocation, 13); // Set the map view to user's location
            L.marker(userLocation).addTo(map)
                .bindPopup("You are here").openPopup();
        }, function(error) {
            console.error('Error getting user location:', error.message);
            // Default to Nairobi if user's location is not available
            var nairobiLocation = [-1.286389, 36.817223];
            map.setView(nairobiLocation, 13);

            L.marker(nairobiLocation).addTo(map)
                .bindPopup("Nairobi").openPopup();
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
        // Default to Nairobi if geolocation is not supported
        var nairobiLocation = [-1.286389, 36.817223];
        map.setView(nairobiLocation, 13);
        
        // Add marker at Nairobi
        L.marker(nairobiLocation).addTo(map)
            .bindPopup("Nairobi").openPopup();    
    }
}

// Call function to center map on user's location
centerMapOnUserLocation();
