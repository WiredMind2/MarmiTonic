// D3.js Disjoint Force-Directed Graph Implementation

class D3DisjointForceGraph {
    constructor(containerSelector, width = 800, height = 600) {
        this.container = d3.select(containerSelector);
        this.width = width;
        this.height = height;
        this.simulation = null;
        this.nodes = [];
        this.links = [];
        this.svg = null;
        this.nodeElements = null;
        this.linkElements = null;
        this.forceStrength = 0.1;
        this.distance = 100;
        this.chargeStrength = -50;
        
        this.init();
    }

    init() {
        // Clear container
        this.container.html('');

        // Create SVG
        this.svg = this.container.append('svg')
            .attr('width', this.width)
            .attr('height', this.height)
            .attr('viewBox', [-this.width / 2, -this.height / 2, this.width, this.height])
            .style('background-color', '#fff8e7');

        // Add zoom and pan functionality
        const zoom = d3.zoom()
            .scaleExtent([0.1, 10])
            .on('zoom', (event) => {
                this.svg.selectAll('g').attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Create a group for all graph elements
        this.graphGroup = this.svg.append('g');
    }

    updateData(graphData) {
        if (!graphData || !graphData.nodes || !graphData.links) {
            console.error('Invalid graph data format');
            return;
        }

        this.nodes = graphData.nodes;
        this.links = graphData.links;

        // Stop any existing simulation
        if (this.simulation) {
            this.simulation.stop();
        }

        this.renderGraph();
    }

    renderGraph() {
        // Clear previous elements
        this.graphGroup.selectAll('*').remove();

        // Create simulation with disjoint force layout
        this.simulation = d3.forceSimulation(this.nodes)
            .force('link', d3.forceLink(this.links).id(d => d.id).distance(this.distance))
            .force('charge', d3.forceManyBody().strength(this.chargeStrength))
            .force('x', d3.forceX(0).strength(this.forceStrength))
            .force('y', d3.forceY(0).strength(this.forceStrength))
            .force('center', d3.forceCenter(0, 0))
            .force('collide', d3.forceCollide().radius(20))
            .on('tick', () => this.ticked());

        // Create links
        this.linkElements = this.graphGroup.append('g')
            .selectAll('line')
            .data(this.links)
            .enter().append('line')
            .attr('stroke', '#999')
            .attr('stroke-opacity', 0.6)
            .attr('stroke-width', d => Math.sqrt(d.value || 1));

        // Create nodes with different colors for different types
        this.nodeElements = this.graphGroup.append('g')
            .selectAll('circle')
            .data(this.nodes)
            .enter().append('circle')
            .attr('r', 10)
            .attr('fill', d => this.getNodeColor(d.type))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1.5)
            .call(this.drag(this.simulation));

        // Add tooltips
        this.nodeElements.append('title')
            .text(d => `${d.name} (${d.type})`);

        // Add labels
        this.graphGroup.append('g')
            .selectAll('text')
            .data(this.nodes)
            .enter().append('text')
            .text(d => d.name)
            .attr('font-size', '10px')
            .attr('dx', 15)
            .attr('dy', '.35em')
            .attr('fill', '#333');
    }

    ticked() {
        this.linkElements
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        this.nodeElements
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        this.graphGroup.selectAll('text')
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    }

    drag(simulation) {
        function dragstarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }

        function dragended(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended);
    }

    getNodeColor(type) {
        const colors = {
            'cocktail': '#4e79a7',
            'ingredient': '#f28e2b',
            'unknown': '#e15759',
            'default': '#76b7b2'
        };
        return colors[type] || colors.default;
    }

    // Disjoint graph specific methods
    highlightDisjointComponents() {
        // Find connected components
        const components = this.findConnectedComponents();
        
        // Color nodes by component
        const colorScale = d3.scaleOrdinal(d3.schemeCategory10);
        
        this.nodeElements
            .attr('fill', d => colorScale(components.find(c => c.includes(d.id))?.index || 0));
    }

    findConnectedComponents() {
        // Create adjacency list
        const adj = {};
        this.nodes.forEach(node => {
            adj[node.id] = [];
        });
        
        this.links.forEach(link => {
            adj[link.source.id].push(link.target.id);
            adj[link.target.id].push(link.source.id);
        });

        // Find connected components using BFS
        const visited = new Set();
        const components = [];
        let componentIndex = 0;

        this.nodes.forEach(node => {
            if (!visited.has(node.id)) {
                const component = [];
                const queue = [node.id];
                visited.add(node.id);

                while (queue.length > 0) {
                    const current = queue.shift();
                    component.push(current);

                    adj[current].forEach(neighbor => {
                        if (!visited.has(neighbor)) {
                            visited.add(neighbor);
                            queue.push(neighbor);
                        }
                    });
                }

                components.push({
                    nodes: component,
                    index: componentIndex++
                });
            }
        });

        return components;
    }

    setForceParameters(forceStrength, distance, chargeStrength) {
        this.forceStrength = forceStrength;
        this.distance = distance;
        this.chargeStrength = chargeStrength;
        
        if (this.simulation) {
            this.simulation
                .force('link', d3.forceLink(this.links).id(d => d.id).distance(this.distance))
                .force('charge', d3.forceManyBody().strength(this.chargeStrength))
                .force('x', d3.forceX(0).strength(this.forceStrength))
                .force('y', d3.forceY(0).strength(this.forceStrength))
                .alpha(1).restart();
        }
    }

    destroy() {
        if (this.simulation) {
            this.simulation.stop();
        }
        this.container.html('');
    }
}