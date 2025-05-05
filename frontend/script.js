const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const setupScreen = document.getElementById('setup-screen');
const gameScreen = document.getElementById('game-screen');
const startButton = document.getElementById('start-button');
const usernameInput = document.getElementById('username');
const mapSizeInput = document.getElementById('map-size');
const playerNameDisplay = document.getElementById('player-name-display');
const gameOverMessage = document.getElementById('game-over-message');
const finalScoreDisplay = document.getElementById('final-score');
const setupErrorElement = document.getElementById('setup-error');


// --- Configuration ---
const API_BASE_URL = 'http://127.0.0.1:8000/api';
const POLLING_RATE_HZ = 5;
const POLLING_INTERVAL_MS = 1000 / POLLING_RATE_HZ; // How often to fetch game state

// --- Game State ---
let cellSize = 20; // Default, will be updated based on map size
let boardSize = [10, 10]; // Default, will be updated from backend
let pollingIntervalId = null;   // To manage the polling timer
let currentUsername = '';       // Store username for restart
let currentMapSize = 10;      // Store map size for restart
let gameActive = false;         // Track if game loop should be running
let isKeyListenerActive = false; // Track if the key listener is attached

// --- API Functions ---
async function postData(url = '', data = {}) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            let errorData;
            try {
                 errorData = await response.json(); // Try to get error details
                 // Display backend error message if available
                 throw new Error(errorData.detail || `HTTP error ${response.status}`);
            } catch (e) {
                 // If response is not JSON or doesn't have detail
                 console.error(`HTTP error ${response.status}: Non-JSON response or missing detail.`);
                 throw new Error(`HTTP error ${response.status}`);
            }
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch POST error:', error);
        throw error; // Re-throw to be caught by caller
    }
}

async function getData(url = '') {
     try {
        const response = await fetch(url);
         if (!response.ok) {
             let errorData;
             try {
                 errorData = await response.json(); // Try to get error details
                 // Display backend error message if available
                 throw new Error(errorData.detail || `HTTP error ${response.status}`);
             } catch (e) {
                 // If response is not JSON or doesn't have detail
                 console.error(`HTTP error ${response.status}: Non-JSON response or missing detail.`);
                 throw new Error(`HTTP error ${response.status}`);
             }
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch GET error:', error);
        throw error; // Re-throw to be caught by caller
    }
}


// --- Game Logic ---
function drawBoard(state) {
    boardSize = state.board_size || [10, 10];
    const gridWidth = boardSize[0];
    const gridHeight = boardSize[1];

    // Calculate cell size to fit canvas (e.g., max 500px width/height)
    const maxCanvasWidth = 500;
    const maxCanvasHeight = 500;
    cellSize = Math.min(Math.floor(maxCanvasWidth / gridWidth), Math.floor(maxCanvasHeight / gridHeight));

    canvas.width = gridWidth * cellSize;
    canvas.height = gridHeight * cellSize;

    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw grid
    ctx.strokeStyle = '#333';
    for (let x = 0; x < gridWidth; x++) {
        for (let y = 0; y < gridHeight; y++) {
            ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
        }
    }

    // Draw snake
    ctx.fillStyle = '#0f0';
    state.snake.forEach(segment => {
        const [x, y] = segment;
        const canvasY = (gridHeight - 1 - y); // Invert Y coordinate
        ctx.fillRect(x * cellSize, canvasY * cellSize, cellSize, cellSize);
        ctx.strokeStyle = '#0a0';
        ctx.strokeRect(x * cellSize, canvasY * cellSize, cellSize, cellSize);
    });

    // Draw food
    ctx.fillStyle = '#f00';
    if (state.food && state.food.length === 2) {
        const [fx, fy] = state.food;
         const foodCanvasY = (gridHeight - 1 - fy); // Invert Y coordinate
        ctx.fillRect(fx * cellSize, foodCanvasY * cellSize, cellSize, cellSize);
    }

    // Update score display using scoreElement
    scoreElement.textContent = state.score;
}


// Function to fetch and update game state
async function pollGameState() {
    // Stop polling if the game becomes inactive *during* polling
    if (!gameActive) {
        // We only stop the *timer* here, not the listener
        if (pollingIntervalId) {
            clearInterval(pollingIntervalId);
            pollingIntervalId = null;
            console.log("Polling interval stopped because game became inactive.");
        }
        return;
    }

    try {
        const currentState = await getData(`${API_BASE_URL}/game/state`);

        // Check if game is still active *after* getting state (could have changed)
        if (!gameActive) return;

        drawBoard(currentState);
        scoreElement.textContent = currentState.score;

        if (currentState.game_over) {
            console.log("Game Over! Score:", currentState.score);
            gameActive = false; // Mark game as inactive
            // Only stop the polling *timer*. The listener stays active for 'R'.
            if (pollingIntervalId) {
                 clearInterval(pollingIntervalId);
                 pollingIntervalId = null;
                 console.log("Polling interval stopped due to game over.");
            }

            finalScoreDisplay.textContent = currentState.score;
            gameOverMessage.querySelector('p:last-child').textContent = 'Press R to Restart'; // Ensure message includes 'R' instruction
            gameOverMessage.style.display = 'block';

        } else {
            // Game is active and not over, polling continues via setInterval
        }
    } catch (error) {
        console.error('Error polling game state:', error);
        gameActive = false; // Mark game as inactive on error
        // Only stop the polling *timer*. The listener stays active for 'R'.
        if (pollingIntervalId) {
             clearInterval(pollingIntervalId);
             pollingIntervalId = null;
             console.log("Polling interval stopped due to error.");
        }
        // Display error message
        setupErrorElement.textContent = `Error updating game: ${error.message}. Try restarting (R).`;
        gameOverMessage.querySelector('h2').textContent = 'Connection Error!';
        finalScoreDisplay.textContent = scoreElement.textContent; // Show last known score
        gameOverMessage.querySelector('p:last-child').textContent = `Error: ${error.message}. Press R to try restarting.`;
        gameOverMessage.style.display = 'block';
    }
}

// Function to start polling
function startPolling() {
    // Clear any previous interval *before* starting a new one
    if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
    }
    console.log("Starting game state polling...");
    gameActive = true; // Mark game as active
    gameOverMessage.style.display = 'none'; // Hide game over message
    setupErrorElement.textContent = ''; // Clear any previous errors

    // Attach the key listener *if it's not already active*
    // This ensures it's only added once per game session
    if (!isKeyListenerActive) {
        document.addEventListener('keydown', handleKeydown);
        isKeyListenerActive = true;
        console.log("Keydown listener attached.");
    }

    pollGameState(); // Run immediately once
    pollingIntervalId = setInterval(pollGameState, POLLING_INTERVAL_MS); // Poll repeatedly
}

// Function to stop polling *timer* (listener remains)
function stopPollingTimer() {
    if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
        console.log("Polling interval stopped.");
    }
    // Do NOT remove the keydown listener here anymore
}


// --- Event Listeners ---

// Keyboard listener (Handles keys regardless of polling state)
async function handleKeydown(event) {
    // --- Restart Logic (Works even if gameActive is false) ---
    if (event.key.toLowerCase() === 'r') {
        event.preventDefault(); // Prevent default 'R' behavior
        if (!currentUsername) {
            console.log("Cannot restart, username missing.");
            setupErrorElement.textContent = "Cannot restart: Username not set.";
            return;
        }

        console.log('R key pressed. Attempting to restart game...');
        // Stop any potentially running *timer* before restarting
        stopPollingTimer();
        gameActive = false; // Ensure game is marked inactive before restart attempt

        try {
            const initialState = await postData(`${API_BASE_URL}/game/start`, {
                username: currentUsername,
                map_size: currentMapSize,
            });
            console.log('Game restarted successfully. Initial state:', initialState);

            // Reset UI for new game
            setupScreen.style.display = 'none';
            gameScreen.style.display = 'block';
            gameOverMessage.style.display = 'none';
            scoreElement.textContent = initialState.score;
            drawBoard(initialState);

            // Start polling for the new game session
            startPolling(); // This will set gameActive = true and start the timer

        } catch (error) {
            console.error('Failed to restart game:', error);
            setupErrorElement.textContent = `Failed to restart game: ${error.message || error}`;
            gameActive = false; // Ensure game stays inactive on failure
            // Don't start polling on failure
        }
        return; // Don't process movement keys if 'R' was pressed
    }

    // --- Movement Logic (Only process if gameActive is true) ---
    if (!gameActive) {
        // console.log("Movement key ignored: game not active."); // Optional log
        return;
    }

    let direction = null;
    switch (event.key) {
        case 'ArrowUp': case 'w': case 'W': direction = 'up'; break;
        case 'ArrowDown': case 's': case 'S': direction = 'down'; break;
        case 'ArrowLeft': case 'a': case 'A': direction = 'left'; break;
        case 'ArrowRight': case 'd': case 'D': direction = 'right'; break;
        default: return; // Ignore other keys
    }

    if (direction) {
        event.preventDefault(); // Prevent arrow keys from scrolling
        try {
            // Send move command (fire and forget)
            postData(`${API_BASE_URL}/game/move`, { direction });
        } catch (error) {
            // Log error, but polling should eventually correct state
            console.error('Failed to send move:', error);
        }
    }
}


// Start Button listener
startButton.addEventListener('click', async () => {
    const username = usernameInput.value.trim();
    const mapSize = parseInt(mapSizeInput.value, 10);

    setupErrorElement.textContent = ''; // Clear previous errors

    // Validation
    if (!username) {
        setupErrorElement.textContent = 'Please enter a username.'; return;
    }
    if (isNaN(mapSize) || mapSize < 5 || mapSize > 25) {
        setupErrorElement.textContent = 'Map size must be between 5 and 25.'; return;
    }

    console.log(`Attempting to start game for ${username} with size ${mapSize}`);
    // Stop any previous polling timer and mark game inactive before starting
    stopPollingTimer();
    gameActive = false;

    try {
        const initialState = await postData(`${API_BASE_URL}/game/start`, {
            username: username,
            map_size: mapSize,
        });
        console.log("Game started successfully on backend. Initial state:", initialState);

        currentUsername = username;
        currentMapSize = mapSize;

        playerNameDisplay.textContent = currentUsername;
        setupScreen.style.display = 'none';
        gameScreen.style.display = 'block';
        gameOverMessage.style.display = 'none';
        scoreElement.textContent = initialState.score;

        drawBoard(initialState);
        startPolling(); // Start polling and attach listener (if not already attached)

    } catch (error) {
        console.error("Failed to start game:", error);
        setupErrorElement.textContent = `Failed to start game: ${error.message || error}`;
        gameActive = false; // Ensure game stays inactive
        // Don't start polling on failure
    }
});

// --- Initial Setup ---
function initializeUI() {
    setupScreen.style.display = 'block';
    gameScreen.style.display = 'none';
    gameOverMessage.style.display = 'none';
    gameActive = false;
    stopPollingTimer(); // Ensure no timer is running initially
    // Remove listener on full page load/reset if it was somehow left attached
    if (isKeyListenerActive) {
        document.removeEventListener('keydown', handleKeydown);
        isKeyListenerActive = false;
        console.log("Keydown listener removed on initial setup.");
    }
}

// Run initial setup when the script loads
initializeUI();