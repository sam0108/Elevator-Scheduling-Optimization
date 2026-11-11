const jsonFilePath = {
    'scan': '../animation_log/simulation_log_scan_algorithm.json',
    'scan_plus': '../animation_log/simulation_log_scan_plus_algorithm.json',
}

// Global variables
let simulationData = null;
let currentStep = 0;
let maxStep = 0;
let isPlaying = false;
let playInterval = null;
let playSpeed = 400; // milliseconds
let currentAlgorithm = Object.keys(jsonFilePath)[0];

// Select elements
const algorithmSelect = document.getElementById('algorithmSelect');
const resetBtn = document.getElementById('resetBtn');
const prevBtn = document.getElementById('prevBtn');
const playPauseBtn = document.getElementById('playPauseBtn');
const nextBtn = document.getElementById('nextBtn');
const stepDisplay = document.getElementById('stepDisplay');
const floorsContainer = document.getElementById('floors');
const elevatorShaftsContainer = document.getElementById('elevatorShafts');
const infoPanel = document.getElementById('infoPanel')

// Load JSON data
async function loadData(algorithm) {
    try {
        // Load simulation data based on selected algorithm
        const response = await fetch(jsonFilePath[algorithm]);
        const jsonData = await response.json();

        simulationData = jsonData;
        maxStep = Object.keys(simulationData).length - 1;
        initializeSimulation();
        renderStep(currentStep);

    } catch (error) {
        console.error('Error loading data:', error);
        alert('Error loading simulation data!');
    }
}

// Initialize simulation
function initializeSimulation() {
    // Get floor and elevator count from first step
    const firstStep = simulationData['0'];
    const floorCount = firstStep.floors.length;
    const elevatorCount = firstStep.elevators.length;

    // Generate floors
    floorsContainer.innerHTML = '';
    for (let i = 0; i < floorCount; i++) {
        const floorEl = document.createElement('div');
        floorEl.className = 'floor';
        floorEl.innerHTML = `
      <span class="floor-number">${i}</span>
      <span class="waiting" id="floor-${i}-waiting"></span>
    `;
        floorsContainer.appendChild(floorEl);
    }

    // Generate elevator shafts
    elevatorShaftsContainer.innerHTML = '';
    for (let i = 0; i < elevatorCount; i++) {
        const shaftEl = document.createElement('div');
        shaftEl.className = 'elevator-shaft';

        const elevatorEl = document.createElement('div');
        elevatorEl.id = `elevator-${i}`;
        elevatorEl.className = 'elevator';
        
        // Add doors to elevator
        elevatorEl.innerHTML = `
            <div class="elevator-doors">
                <div class="door left-door"></div>
                <div class="door right-door"></div>
            </div>
            <div class="elevator-content">0</div>
        `;

        shaftEl.appendChild(elevatorEl);
        elevatorShaftsContainer.appendChild(shaftEl);
    }

    // Set elevator height
    const floorHeight = 100 / floorCount;
    document.querySelectorAll('.elevator').forEach(el => {
        el.style.height = `${floorHeight}%`;
    });
    
    // Check screen size and adjust if necessary
    adjustForScreenSize();
    
    // Add resize event listener for responsiveness
    window.addEventListener('resize', adjustForScreenSize);
}

// Adjust elements based on screen size
function adjustForScreenSize() {
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
    
    // Adjust the waiting text for smaller screens
    const waitingElements = document.querySelectorAll('.waiting');
    waitingElements.forEach(el => {
        const text = el.textContent;
        if (isMobile && text.includes('Waiting: ')) {
            el.textContent = text.replace('Waiting: ', '');
        } else if (!isMobile && !text.includes('Waiting: ') && text !== '') {
            el.textContent = 'Waiting: ' + text;
        }
    });
}

// Keep track of previous elevator positions for smooth transitions
let previousElevatorPositions = [];

// Render current step
function renderStep(step) {
    if (!simulationData || !simulationData[step]) return;

    const data = simulationData[step];
    const { elevators, floors, energy_consumption } = data;

    // Initialize previous positions array if needed
    if (previousElevatorPositions.length === 0) {
        previousElevatorPositions = elevators.map(e => e.curr_floor);
    }

    // Update step display
    stepDisplay.textContent = `Step: ${step}`;

    // Update waiting people on floors
    floors.forEach(floor => {
        const waitingEl = document.getElementById(`floor-${floor.floor}-waiting`);
        if (waitingEl) {
            // Adapt text based on screen size
            if (window.innerWidth < 768) {
                waitingEl.textContent = `${floor.waiting}`;
            } else {
                waitingEl.textContent = `Waiting: ${floor.waiting}`;
            }
            
            // Change color based on waiting count
            if (floor.waiting === 0) {
                waitingEl.classList.add('no-waiting');
            } else {
                waitingEl.classList.remove('no-waiting');
            }
        }
    });

    // Update elevator positions and information
    elevators.forEach((elevator, index) => {
        const elevatorEl = document.getElementById(`elevator-${index}`);
        if (!elevatorEl) return;

        const floorCount = floors.length;
        const floorHeight = 100 / floorCount;
        const bottomPosition = elevator.curr_floor * floorHeight;

        // Smooth animation for elevator movement
        const currentBottom = parseFloat(elevatorEl.style.bottom) || 0;
        
        if (Math.abs(currentBottom - bottomPosition) > 0.1) {
            if (Math.abs(currentBottom - bottomPosition) > floorHeight * 2) {
                elevatorEl.style.transition = 'none';
                setTimeout(() => {
                    elevatorEl.style.transition = 'bottom 0.5s linear';
                }, 10);
            }
        }
        
        elevatorEl.style.bottom = `${bottomPosition}%`;
        
        // Set elevator status (moving or open)
        const isOpen = elevator.curr_direction === 'OPEN';
        elevatorEl.classList.toggle('moving', !isOpen);
        
        // Control door animation
        const leftDoor = elevatorEl.querySelector('.left-door');
        const rightDoor = elevatorEl.querySelector('.right-door');
        
        if (isOpen) {
            leftDoor.classList.add('door-open');
            rightDoor.classList.add('door-open');
        } else {
            leftDoor.classList.remove('door-open');
            rightDoor.classList.remove('door-open');
        }
        
        // Update passenger count
        const contentEl = elevatorEl.querySelector('.elevator-content');
        contentEl.textContent = elevator.num_people;
    });

    // Update info panel
    updateInfoPanel(step, data);

    // Update button states
    prevBtn.disabled = step <= 0;
    nextBtn.disabled = step >= maxStep;
}

// Update information panel
function updateInfoPanel(step, data) {
    const { elevators, energy_consumption } = data;

    // Convert energy consumption to kWh for display
    const energyConsumptionInKWh = energy_consumption / 3.6e6; // Convert to kWh

    let html = `
    <div class="energy-info">Energy Consumption: ${energyConsumptionInKWh.toLocaleString()} kWh</div>
  `;

    elevators.forEach((elevator, index) => {
        const status = elevator.dest_floor !== null ?
            `Moving (to floor ${elevator.dest_floor})` :
            'Idle';

        html += `
      <div class="elevator-info">
        <h3>Elevator ${index + 1}</h3>
        <p>Current Floor: ${elevator.curr_floor}</p>
        <p>Status: ${status}</p>
        <p>Passengers: ${elevator.num_people}</p>
        <p>Scheduled Floors:</p>
        <div class="scheduled-list">
          ${elevator.scheduled_list.map(floor =>
            `<span class="floor-item">${floor}</span>`
        ).join('')}
        </div>
      </div>
    `;
    });

    infoPanel.innerHTML = html;
}

// Play control
function togglePlay() {
    isPlaying = !isPlaying;

    if (isPlaying) {
        playPauseBtn.textContent = 'Pause';
        playInterval = setInterval(() => {
            if (currentStep < maxStep) {
                if (simulationData && simulationData[currentStep]) {
                    previousElevatorPositions = simulationData[currentStep].elevators.map(e => e.curr_floor);
                }
                
                currentStep++;
                renderStep(currentStep);
            } else {
                togglePlay(); // Auto stop
            }
        }, playSpeed);
    } else {
        playPauseBtn.textContent = 'Play';
        clearInterval(playInterval);
    }
}

// Move forward one step
function nextStep() {
    if (currentStep < maxStep) {
        if (simulationData && simulationData[currentStep]) {
            previousElevatorPositions = simulationData[currentStep].elevators.map(e => e.curr_floor);
        }
        
        currentStep++;
        renderStep(currentStep);
    }
}

// Move back one step
function prevStep() {
    if (currentStep > 0) {
        if (simulationData && simulationData[currentStep]) {
            previousElevatorPositions = simulationData[currentStep].elevators.map(e => e.curr_floor);
        }
        
        currentStep--;
        renderStep(currentStep);
    }
}

function resetSimulation() {
    currentStep = 0;
    previousElevatorPositions = [];
    renderStep(currentStep);
    if (isPlaying) {
        togglePlay(); // Stop playing if currently playing
    }
}

// Event listeners
resetBtn.addEventListener('click', resetSimulation);
playPauseBtn.addEventListener('click', togglePlay);
nextBtn.addEventListener('click', nextStep);
prevBtn.addEventListener('click', prevStep);

// Handle algorithm selection
algorithmSelect.addEventListener('change', (e) => {
    currentAlgorithm = e.target.value;
    resetSimulation();
    loadData(currentAlgorithm);
});

// Load data and start simulation
window.addEventListener('DOMContentLoaded', () => {
    loadData(currentAlgorithm);
});