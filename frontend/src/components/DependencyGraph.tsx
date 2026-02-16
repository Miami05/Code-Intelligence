/**
 * Dependency Graph Visualization Component - Tailwind CSS Version
 * Uses D3.js force-directed graph
 */

import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

interface GraphNode {
  id: string;
  label: string;
  type: 'internal' | 'external';
  file?: string | null;
}

interface GraphEdge {
  source: string;
  target: string;
  label?: string;
}

interface DependencyGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

const DependencyGraph: React.FC<DependencyGraphProps> = ({ nodes, edges }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;

    // Clear previous graph
    d3.select(svgRef.current).selectAll('*').remove();

    const width = 800;
    const height = 600;

    const svg = d3
      .select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Create links data
    const links = edges.map((e) => ({
      source: e.source,
      target: e.target,
      label: e.label,
    }));

    // Create nodes data
    const nodeData = nodes.map((n) => ({
      id: n.id,
      label: n.label,
      type: n.type,
      file: n.file,
    }));

    // Create force simulation
    const simulation = d3
      .forceSimulation(nodeData as any)
      .force(
        'link',
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide(40));

    // Add arrow markers
    svg
      .append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#999');

    // Add links
    const link = svg
      .append('g')
      .selectAll('line')
      .data(links)
      .enter()
      .append('line')
      .attr('stroke', '#999')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)');

    // Add nodes
    const node = svg
      .append('g')
      .selectAll('g')
      .data(nodeData)
      .enter()
      .append('g')
      .call(
        d3
          .drag()
          .on('start', dragstarted)
          .on('drag', dragged)
          .on('end', dragended) as any
      );

    // Add circles to nodes
    node
      .append('circle')
      .attr('r', 20)
      .attr('fill', (d: any) => (d.type === 'external' ? '#ccc' : '#2563eb'))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer');

    // Add labels to nodes
    node
      .append('text')
      .text((d: any) => d.label)
      .attr('font-size', 12)
      .attr('dx', 25)
      .attr('dy', 4)
      .attr('fill', '#334155')
      .style('pointer-events', 'none');

    // Add tooltips
    node.append('title').text((d: any) => `${d.label}\n${d.file || 'External'}`);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    // Cleanup
    return () => {
      simulation.stop();
    };
  }, [nodes, edges]);

  if (nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600">
        <p className="text-slate-600 dark:text-slate-400">No graph data available</p>
      </div>
    );
  }

  return (
    <div className="flex justify-center bg-slate-50 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-600 p-4">
      <svg ref={svgRef} className="max-w-full" />
    </div>
  );
};

export default DependencyGraph;
