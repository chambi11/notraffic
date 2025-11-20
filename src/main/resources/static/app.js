// API Configuration
const API_BASE_URL = 'http://localhost:8080/api/polygons';

// State
let polygons = [];
let currentPolygon = [];
let isDrawing = false;
let highlightedPolygonId = null;

// Canvas elements
const canvas = document.getElementById('polygonCanvas');
const ctx = canvas.getContext('2d');
const polygonNameInput = document.getElementById('polygonName');
const startDrawingBtn = document.getElementById('startDrawing');
const finishPolygonBtn = document.getElementById('finishPolygon');
const cancelDrawingBtn = document.getElementById('cancelDrawing');
const clearCanvasBtn = document.getElementById('clearCanvas');
const polygonListDiv = document.getElementById('polygonList');
const loadingOverlay = document.getElementById('loadingOverlay');

// Background image loader
let backgroundLoaded = false;
const backgroundImage = new Image();
backgroundImage.crossOrigin = 'anonymous';
backgroundImage.src = 'https://picsum.photos/1920/1080';

backgroundImage.onload = () => {
    backgroundLoaded = true;
    drawCanvas();
};

backgroundImage.onerror = () => {
    backgroundLoaded = false;
    drawCanvas();
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPolygons();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    startDrawingBtn.addEventListener('click', startDrawing);
    finishPolygonBtn.addEventListener('click', finishPolygon);
    cancelDrawingBtn.addEventListener('click', cancelDrawing);
    clearCanvasBtn.addEventListener('click', clearCanvas);
    canvas.addEventListener('click', handleCanvasClick);
}

function startDrawing() {
    const name = polygonNameInput.value.trim();
    if (!name) {
        alert('Please enter a polygon name');
        return;
    }

    isDrawing = true;
    currentPolygon = [];

    startDrawingBtn.disabled = true;
    finishPolygonBtn.disabled = true;  // Disabled until 3 points are drawn
    cancelDrawingBtn.disabled = false;
    polygonNameInput.disabled = true;

    drawCanvas();
}

function handleCanvasClick(event) {
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = (event.clientX - rect.left) * scaleX;
    const y = (event.clientY - rect.top) * scaleY;

    currentPolygon.push([x, y]);
    drawCanvas();

    if (currentPolygon.length >= 3) {
        finishPolygonBtn.disabled = false;
    }
}

async function finishPolygon() {
    if (currentPolygon.length < 3) {
        alert('A polygon must have at least 3 points');
        return;
    }

    const name = polygonNameInput.value.trim();

    showLoading(true);

    try {
        const response = await fetch(API_BASE_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                points: currentPolygon
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to create polygon');
        }

        const newPolygon = await response.json();
        polygons.push(newPolygon);

        resetDrawingState();
        drawCanvas();
        updatePolygonList();

        polygonNameInput.value = '';
    } catch (error) {
        alert('Error creating polygon: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function cancelDrawing() {
    currentPolygon = [];
    resetDrawingState();
    drawCanvas();
}

function resetDrawingState() {
    isDrawing = false;
    currentPolygon = [];

    startDrawingBtn.disabled = false;
    finishPolygonBtn.disabled = true;
    cancelDrawingBtn.disabled = true;
    polygonNameInput.disabled = false;
}

function clearCanvas() {
    console.log('Clear Canvas clicked');

    // Clear current drawing
    currentPolygon = [];
    highlightedPolygonId = null;

    // Reset drawing state if currently drawing
    if (isDrawing) {
        console.log('Resetting drawing state');
        resetDrawingState();
    }

    // Redraw canvas
    console.log('Redrawing canvas');
    drawCanvas();

    console.log('Canvas cleared successfully');
}

async function loadPolygons() {
    showLoading(true);

    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) {
            throw new Error('Failed to fetch polygons');
        }

        polygons = await response.json();
        updatePolygonList();
        drawCanvas();
    } catch (error) {
        alert('Error loading polygons: ' + error.message);
    } finally {
        showLoading(false);
    }
}

async function deletePolygon(id) {
    if (!confirm('Are you sure you want to delete this polygon?')) {
        return;
    }

    showLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to delete polygon');
        }

        polygons = polygons.filter(p => p.id !== id);
        if (highlightedPolygonId === id) {
            highlightedPolygonId = null;
        }

        updatePolygonList();
        drawCanvas();
    } catch (error) {
        alert('Error deleting polygon: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function highlightPolygon(id) {
    highlightedPolygonId = highlightedPolygonId === id ? null : id;
    drawCanvas();
    updatePolygonList();
}

function updatePolygonList() {
    if (polygons.length === 0) {
        polygonListDiv.innerHTML = '<p class="no-polygons">No polygons created yet</p>';
        return;
    }

    polygonListDiv.innerHTML = polygons.map(polygon => `
        <div class="polygon-item ${highlightedPolygonId === polygon.id ? 'highlighted' : ''}"
             onclick="highlightPolygon(${polygon.id})">
            <div class="polygon-header">
                <span class="polygon-name">${escapeHtml(polygon.name)}</span>
                <span class="polygon-id">ID: ${polygon.id}</span>
            </div>
            <div class="polygon-points">
                Points: ${polygon.points.length} |
                ${polygon.points.map(p => `[${p[0].toFixed(1)}, ${p[1].toFixed(1)}]`).join(', ')}
            </div>
            <button class="delete-btn" onclick="event.stopPropagation(); deletePolygon(${polygon.id})">
                Delete Polygon
            </button>
        </div>
    `).join('');
}

function drawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (backgroundLoaded) {
        try {
            ctx.drawImage(backgroundImage, 0, 0, canvas.width, canvas.height);
        } catch {
            ctx.fillStyle = "#ffffff";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
    } else {
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    polygons.forEach(polygon => {
        const isHighlighted = polygon.id === highlightedPolygonId;
        drawPolygon(polygon.points, isHighlighted ? '#FF0000' : '#00FF00', isHighlighted);
    });

    if (currentPolygon.length > 0) {
        drawPolygon(currentPolygon, '#0000FF', true, true);
    }
}

function drawPolygon(points, color, isHighlighted, isIncomplete = false) {
    if (points.length === 0) return;

    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);

    for (let i = 1; i < points.length; i++) {
        ctx.lineTo(points[i][0], points[i][1]);
    }

    if (!isIncomplete) {
        ctx.closePath();
    }

    ctx.fillStyle = color + '40';
    ctx.fill();

    ctx.strokeStyle = color;
    ctx.lineWidth = isHighlighted ? 4 : 2;
    ctx.stroke();

    points.forEach((point, index) => {
        ctx.beginPath();
        ctx.arc(point[0], point[1], isHighlighted ? 6 : 4, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#FFFFFF';
        ctx.lineWidth = 2;
        ctx.stroke();

        if (isHighlighted || isIncomplete) {
            ctx.fillStyle = '#FFFFFF';
            ctx.font = 'bold 14px Arial';
            ctx.fillText((index + 1).toString(), point[0] + 10, point[1] - 10);
        }
    });
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
    canvas.classList.toggle('disabled', show);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

window.deletePolygon = deletePolygon;
window.highlightPolygon = highlightPolygon;
