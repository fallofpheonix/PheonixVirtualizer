import React, { useEffect, useRef, useState } from 'react';
import ForceGraph3D from '3d-force-graph';

interface GraphData {
  nodes: any[];
  edges: any[];
}

export const DependencyGraph3D: React.FC<{ data: GraphData }> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    // Transform backend contract into 3D Scene Graph layout
    const sceneData = {
      nodes: data.nodes.map(node => ({
        id: node.id,
        name: node.label,
        val: node.kind === 'FOLDER' || node.kind === 'PROJECT' ? 20 : 5,
        color: getNodeColor(node.status, node.kind),
        kind: node.kind,
        status: node.status,
        path: node.path
      })),
      links: data.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        color: edge.status === 'BROKEN' ? '#ff4d4d' : '#4a5568',
        width: edge.status === 'BROKEN' ? 2 : 0.5
      }))
    };

    // Initialize the 3D Engine
    const Graph = ForceGraph3D()(containerRef.current)
      .graphData(sceneData)
      .nodeColor('color')
      .nodeVal('val')
      .linkSource('source')
      .linkTarget('target')
      .linkColor('color')
      .linkWidth('width')
      .linkOpacity(0.6)
      .nodeLabel(node => `[${(node as any).kind}] ${(node as any).name}`)
      .onNodeClick(node => {
        setSelectedNode(node);
        // Camera focus tracking on selected node
        const distance = 40;
        const distRatio = 1 + distance / Math.hypot((node as any).x || 0, (node as any).y || 0, (node as any).z || 0);
        Graph.cameraPosition(
          { x: (node as any).x * distRatio, y: (node as any).y * distRatio, z: (node as any).z * distRatio },
          node as any,
          1000
        );
      });

    // Handle Window Resize dynamically
    const handleResize = () => {
      Graph.width(containerRef.current?.clientWidth || window.innerWidth);
      Graph.height(containerRef.current?.clientHeight || window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      containerRef.current!.innerHTML = '';
    };
  }, [data]);

  // Status-driven Color Scheme Matrix
  function getNodeColor(status: string, kind: string): string {
    if (kind === 'PROJECT') return '#a855f7'; // Purple core
    if (kind === 'FOLDER') return '#e2e8f0';  // Clean white/gray folders
    if (kind === 'EXTERNAL_PACKAGE') return '#3b82f6'; // Bright blue for vendors/packages
    
    switch (status) {
      case 'VERIFIED': return '#22c55e';   // Green Clean Working connection
      case 'BROKEN': return '#ef4444';     // Red Broken link
      case 'WARNING': return '#eab308';    // Yellow Circular Dependency loop
      default: return '#94a3b8';           // Gray Unresolved dynamic code
    }
  }

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      
      {/* Local Node Inspector HUD Layer */}
      {selectedNode && (
        <div style={{
          position: 'absolute', bottom: '20px', right: '20px', 
          background: 'rgba(26, 26, 26, 0.95)', padding: '20px',
          borderRadius: '8px', border: '1px solid #3f3f46',
          color: '#f4f4f5', width: '300px', fontFamily: 'monospace'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: selectedNode.color }}>{selectedNode.name}</h3>
          <p><strong>Type:</strong> {selectedNode.kind}</p>
          <p><strong>Path:</strong> {selectedNode.path || './'}</p>
          <p><strong>Status:</strong> <span style={{ color: selectedNode.color }}>{selectedNode.status}</span></p>
          <button 
            onClick={() => setSelectedNode(null)}
            style={{
              background: '#3f3f46', border: 'none', color: '#fff',
              padding: '5px 10px', borderRadius: '4px', cursor: 'pointer', marginTop: '10px'
            }}
          >
            Close Inspector
          </button>
        </div>
      )}
    </div>
  );
};
