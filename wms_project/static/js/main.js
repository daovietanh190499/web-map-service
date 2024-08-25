// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize map
    const map = L.map('map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Initialize edit map (hidden by default)
    const editMap = L.map('edit-map').setView([0, 0], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(editMap);

    // Timeline
    const timeline = document.getElementById('timeline');

    // Search
    const searchInput = document.getElementById('search');
    searchInput.addEventListener('input', debounce(searchImages, 300));

    // Upload form
    const uploadForm = document.getElementById('upload-form');
    uploadForm.addEventListener('submit', uploadImage);

    // Load images
    loadImages();

    function loadImages() {
        fetch('/api/images/')
            .then(response => response.json())
            .then(data => {
                data.forEach(addImageToMap);
                updateTimeline(data);
            });
    }

    function addImageToMap(image) {
        const marker = L.marker([image.geolocation.coordinates[1], image.geolocation.coordinates[0]])
            .addTo(map)
            .bindPopup(`
                <img src="${image.image_url}" alt="${image.name}" style="max-width: 200px; max-height: 200px;">
                <h3>${image.name}</h3>
                <p>Date: ${new Date(image.datetime).toLocaleString()}</p>
                <p>Topic: ${image.topic}</p>
                <button onclick="editImage(${image.id})">Edit</button>
            `);
    }

    function updateTimeline(images) {
        timeline.innerHTML = '';
        images.sort((a, b) => new Date(a.datetime) - new Date(b.datetime));
        images.forEach(image => {
            const dot = document.createElement('div');
            dot.className = 'timeline-dot';
            dot.style.left = `${getTimelinePosition(image.datetime)}%`;
            dot.title = `${image.name} - ${new Date(image.datetime).toLocaleString()}`;
            dot.addEventListener('click', () => {
                map.setView([image.geolocation.coordinates[1], image.geolocation.coordinates[0]], 10);
            });
            timeline.appendChild(dot);
        });
    }

    function getTimelinePosition(datetime) {
        const start = new Date(images[0].datetime).getTime();
        const end = new Date(images[images.length - 1].datetime).getTime();
        const current = new Date(datetime).getTime();
        return ((current - start) / (end - start)) * 100;
    }

    function searchImages() {
        const query = searchInput.value;
        fetch(`/api/images/?search=${query}`)
            .then(response => response.json())
            .then(data => {
                map.eachLayer(layer => {
                    if (layer instanceof L.Marker) {
                        map.removeLayer(layer);
                    }
                });
                data.forEach(addImageToMap);
                updateTimeline(data);
            });
    }

    function uploadImage(event) {
        event.preventDefault();
        const formData = new FormData(uploadForm);
        fetch('/api/images/upload_image/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            addImageToMap(data);
            loadImages();
            uploadForm.reset();
        })
        .catch(error => console.error('Error:', error));
    }

    function editImage(imageId) {
        document.getElementById('edit-map').style.display = 'block';
        // Load image data and initialize mask editing
        fetch(`/api/images/${imageId}/`)
            .then(response => response.json())
            .then(image => {
                editMap.setView([image.geolocation.coordinates[1], image.geolocation.coordinates[0]], 10);
                let mask = [];
                editMap.on('click', e => {
                    mask.push([e.latlng.lat, e.latlng.lng]);
                    L.polyline(mask, {color: 'red'}).addTo(editMap);
                });
                // Add save button
                const saveButton = L.control({position: 'topright'});
                saveButton.onAdd = function(map) {
                    const div = L.DomUtil.create('div', 'save-button');
                    div.innerHTML = '<button onclick="saveMask(' + imageId + ')">Save Mask</button>';
                    return div;
                };
                saveButton.addTo(editMap);
            });
    }

    function saveMask(imageId) {
        // Implement mask saving logic here
        console.log('Saving mask for image', imageId);
        // After saving, hide edit map
        document.getElementById('edit-map').style.display = 'none';
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
});