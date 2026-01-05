// Data visualization utilities
let d3Graph = null;

function visualizeGraph(data) {
    // Initialize D3.js visualization
    if (!d3Graph) {
        d3Graph = new D3DisjointForceGraph('#graph-container', 1000, 800);
        setupControls();
    }
    
    // Update graph data
    d3Graph.updateData(data);
    
    // Log data for debugging
    console.log("Visualizing graph:", data);
}

function calculateMetrics(data) {
    // Calculate basic graph metrics
    const metrics = {};
    
    if (data && data.nodes && data.links) {
        metrics.numNodes = data.nodes.length;
        metrics.numLinks = data.links.length;
        
        // Count by type
        const typeCounts = {};
        data.nodes.forEach(node => {
            typeCounts[node.type] = (typeCounts[node.type] || 0) + 1;
        });
        metrics.typeCounts = typeCounts;
    }
    
    console.log("Calculating metrics:", metrics);
    return metrics;
}

function setupControls() {
    // Highlight components button
    document.getElementById('highlight-components')?.addEventListener('click', () => {
        if (d3Graph) {
            d3Graph.highlightDisjointComponents();
        }
    });
    
    // Force strength control
    document.getElementById('force-strength')?.addEventListener('input', (e) => {
        const forceStrength = parseFloat(e.target.value);
        const distance = parseInt(document.getElementById('distance')?.value || '100');
        const charge = parseInt(document.getElementById('charge')?.value || '-50');
        
        if (d3Graph) {
            d3Graph.setForceParameters(forceStrength, distance, charge);
        }
    });
    
    // Distance control
    document.getElementById('distance')?.addEventListener('input', (e) => {
        const forceStrength = parseFloat(document.getElementById('force-strength')?.value || '0.1');
        const distance = parseInt(e.target.value);
        const charge = parseInt(document.getElementById('charge')?.value || '-50');
        
        if (d3Graph) {
            d3Graph.setForceParameters(forceStrength, distance, charge);
        }
    });
    
    // Charge control
    document.getElementById('charge')?.addEventListener('input', (e) => {
        const forceStrength = parseFloat(document.getElementById('force-strength')?.value || '0.1');
        const distance = parseInt(document.getElementById('distance')?.value || '100');
        const charge = parseInt(e.target.value);
        
        if (d3Graph) {
            d3Graph.setForceParameters(forceStrength, distance, charge);
        }
    });
}

// Cleanup function
function cleanupVisualization() {
    if (d3Graph) {
        d3Graph.destroy();
        d3Graph = null;
    }
}