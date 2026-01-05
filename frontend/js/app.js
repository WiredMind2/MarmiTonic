// Main application logic
console.log("MarmiTonic app initialized");

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    
    // Check if we're on the insights page
    if (window.location.pathname.includes('insights.html')) {
        loadGraphVisualization();
    }
    
    // Add event listeners or other initialization logic here
});

async function loadGraphVisualization() {
    try {
        console.log("Loading graph visualization...");
        
        // Fetch graph data from backend
        const response = await fetch('http://localhost:8000/insights/visualization');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const graphData = await response.json();
        console.log("Graph data received:", graphData);
        
        // Visualize the graph
        visualizeGraph(graphData);
        
        // Calculate and display metrics
        const metrics = calculateMetrics(graphData);
        console.log("Graph metrics:", metrics);
        
    } catch (error) {
        console.error("Failed to load graph visualization:", error);
        // Show error to user
        const container = document.getElementById('graph-container');
        if (container) {
            container.innerHTML = `<div class="error">Failed to load graph visualization. Please try again later.</div>`;
        }
    }
}