import React, { useEffect, useRef, useState, useMemo } from 'react';
import ForceGraph3D from '3d-force-graph';

interface GraphData {
  nodes: any[];
  edges: any[];
}

export const DependencyGraph3D: React.FC<{ data: GraphData }> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [hoverNode, setHoverNode] = useState<any>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [analyzing, setAiAnalyzing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    VERIFIED: true,
    BROKEN: true,
    WARNING: true,
    EXTERNAL_PACKAGE: true
  });

  // O(1) Adjacency Map Pre-computation
  const processedData = useMemo(() => {
    if (!data) return { nodes: [], links: [] };

    // Filter nodes based on state
    const filteredNodes = data.nodes.filter(node => {
      if (node.kind === 'EXTERNAL_PACKAGE') return filters.EXTERNAL_PACKAGE;
      return filters[node.status as keyof typeof filters] !== false;
    });

    const nodeIds = new Set(filteredNodes.map(n => n.id));

    // Filter edges to only include visible nodes
    const filteredEdges = data.edges.filter(edge => 
      nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );

    const nodes = filteredNodes.map(node => ({
      ...node,
      name: node.label,
      neighbors: new Set<string>(),
      links: [] as any[]
    }));

    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    filteredEdges.forEach(edge => {
      const s = nodeMap.get(edge.source);
      const t = nodeMap.get(edge.target);
      if (s && t) {
        s.neighbors.add(t.id);
        t.neighbors.add(s.id);
        s.links.push(edge);
        t.links.push(edge);
      }
    });

    return { 
      nodes, 
      links: filteredEdges.map(edge => ({
        ...edge,
        source: edge.source,
        target: edge.target
      }))
    };
  }, [data, filters]);

  const analyzeWithAI = async (violationId: string) => {
    setAiAnalyzing(true);
    setAiAnalysis(null);
    try {
      const jobId = "default-project"; 
      const response = await fetch(`/api/job/${jobId}/analyze-violation/${violationId}`, {
        method: 'POST'
      });
      const resData = await response.json();
      setAiAnalysis(resData.analysis);
    } catch (err) {
      console.error("AI Analysis failed:", err);
      setAiAnalysis("Failed to generate AI analysis.");
    } finally {
      setAiAnalyzing(false);
    }
  };

  useEffect(() => {
    if (!containerRef.current || !processedData.nodes.length) return;

    // Transform backend contract into 3D Scene Graph layout
    const sceneData = {
      nodes: processedData.nodes.map(node => ({
        ...node,
        val: node.kind === 'FOLDER' || node.kind === 'PROJECT' ? 20 : 5,
        color: getNodeColor(node.status, node.kind)
      })),
      links: processedData.links.map(edge => ({
        ...edge,
        color: edge.status === 'BROKEN' ? '#ff4d4d' : '#4a5568',
        width: edge.status === 'BROKEN' ? 2 : 0.5
      }))
    };

    // Initialize the 3D Engine
    const Graph = ForceGraph3D()(containerRef.current)
      .graphData(sceneData)
      .nodeColor(node => {
        const n = node as any;
        if (selectedNode || hoverNode) {
          const isNeighbor = (selectedNode?.neighbors?.has(n.id)) || (hoverNode?.neighbors?.has(n.id));
          const isSelected = selectedNode?.id === n.id || hoverNode?.id === n.id;
          return isSelected || isNeighbor ? n.color : 'rgba(63, 63, 70, 0.2)';
        }
        return n.color;
      })
      .linkColor(link => {
        const l = link as any;
        if (selectedNode || hoverNode) {
          const isRelated = selectedNode?.id === l.source.id || selectedNode?.id === l.target.id ||
                           hoverNode?.id === l.source.id || hoverNode?.id === l.target.id;
          return isRelated ? l.color : 'rgba(63, 63, 70, 0.1)';
        }
        return l.color;
      })
      .nodeVal('val')
      .linkWidth(link => {
        const l = link as any;
        if (selectedNode || hoverNode) {
          const isRelated = selectedNode?.id === l.source.id || selectedNode?.id === l.target.id ||
                           hoverNode?.id === l.source.id || hoverNode?.id === l.target.id;
          return isRelated ? (l.width * 2) : 0.2;
        }
        return l.width;
      })
      .linkOpacity(0.6)
      .nodeLabel(node => `[${(node as any).kind}] ${(node as any).name}`)
      .onNodeClick(node => {
        const n = node as any;
        setSelectedNode(n);
        setAiAnalysis(null);
        // Camera focus tracking on selected node
        const distance = 60;
        const distRatio = 1 + distance / Math.hypot(n.x || 0, n.y || 0, n.z || 0);
        Graph.cameraPosition(
          { x: n.x * distRatio, y: n.y * distRatio, z: n.z * distRatio },
          n,
          1000
        );
      })
      .onNodeHover(node => {
        setHoverNode(node || null);
      });

    graphRef.current = Graph;

    const handleResize = () => {
      Graph.width(containerRef.current?.clientWidth || window.innerWidth);
      Graph.height(containerRef.current?.clientHeight || window.innerHeight);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      containerRef.current!.innerHTML = '';
    };
  }, [processedData, selectedNode, hoverNode]);

  function getNodeColor(status: string, kind: string): string {
    if (kind === 'PROJECT') return '#a855f7';
    if (kind === 'FOLDER') return '#e2e8f0';
    if (kind === 'EXTERNAL_PACKAGE') return '#3b82f6';
    
    switch (status) {
      case 'VERIFIED': return '#22c55e';
      case 'BROKEN': return '#ef4444';
      case 'WARNING': return '#eab308';
      default: return '#94a3b8';
    }
  }

  const handleCloseInspector = () => {
    setSelectedNode(null);
    setAiAnalysis(null);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const match = processedData.nodes.find(n => 
      n.label.toLowerCase().includes(searchQuery.toLowerCase())
    );
    if (match && graphRef.current) {
      setSelectedNode(match);
      const distance = 80;
      const distRatio = 1 + distance / Math.hypot(match.x || 0, match.y || 0, match.z || 0);
      graphRef.current.cameraPosition(
        { x: (match.x || 0) * distRatio, y: (match.y || 0) * distRatio, z: (match.z || 0) * distRatio },
        match,
        1500
      );
    }
  };

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative', background: '#09090b' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      {/* TOP-LEFT SEARCH HUD */}
      <div style={{
        position: 'absolute', top: '80px', left: '15px', zIndex: 10,
        width: '280px'
      }}>
        <form onSubmit={handleSearch}>
          <input 
            type="text" 
            placeholder="Search nodes (e.g. auth.py)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%', background: 'rgba(24, 24, 27, 0.8)', 
              border: '1px solid #27272a', borderRadius: '6px',
              padding: '10px 15px', color: '#fff', outline: 'none',
              fontFamily: 'monospace'
            }}
          />
        </form>
      </div>

      {/* BOTTOM-LEFT FILTER LEGEND */}
      <div style={{
        position: 'absolute', bottom: '20px', left: '20px', zIndex: 10,
        background: 'rgba(24, 24, 27, 0.85)', backdropFilter: 'blur(4px)',
        padding: '15px', borderRadius: '8px', border: '1px solid #27272a',
        color: '#f4f4f5', fontFamily: 'monospace', width: '220px'
      }}>
        <div style={{ marginBottom: '10px', fontSize: '12px', color: '#71717a' }}>FILTERS</div>
        {(['VERIFIED', 'BROKEN', 'WARNING', 'EXTERNAL_PACKAGE'] as const).map(f => (
          <label key={f} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', cursor: 'pointer' }}>
            <input 
              type="checkbox" 
              checked={filters[f]} 
              onChange={() => setFilters(prev => ({ ...prev, [f]: !prev[f] }))}
              style={{ marginRight: '10px' }}
            />
            <span style={{ fontSize: '13px', color: filters[f] ? '#fff' : '#52525b' }}>
              <span style={{ color: getNodeColor(f, f === 'EXTERNAL_PACKAGE' ? f : 'FILE'), marginRight: '6px' }}>●</span>
              {f.replace('_', ' ')}
            </span>
          </label>
        ))}
      </div>
      
      {/* Node Inspector HUD Layer */}
      {selectedNode && (
        <div style={{
          position: 'absolute', bottom: '20px', right: '20px', 
          background: 'rgba(26, 26, 26, 0.95)', padding: '20px',
          borderRadius: '8px', border: '1px solid #3f3f46',
          color: '#f4f4f5', width: '350px', maxHeight: '80vh', 
          overflowY: 'auto', fontFamily: 'monospace'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: getNodeColor(selectedNode.status, selectedNode.kind) }}>{selectedNode.name}</h3>
          <p><strong>Type:</strong> {selectedNode.kind}</p>
          <p><strong>Path:</strong> {selectedNode.path || './'}</p>
          <p><strong>Status:</strong> <span style={{ color: getNodeColor(selectedNode.status, selectedNode.kind) }}>{selectedNode.status}</span></p>
          
          {(selectedNode.status === 'WARNING' || selectedNode.status === 'BROKEN') && (
            <div style={{ marginTop: '15px', borderTop: '1px solid #3f3f46', paddingTop: '15px' }}>
              <button 
                onClick={() => analyzeWithAI(selectedNode.id)}
                disabled={analyzing}
                style={{
                  background: analyzing ? '#1a1a1a' : '#a855f7', 
                  border: 'none', color: '#fff',
                  padding: '8px 12px', borderRadius: '4px', cursor: 'pointer',
                  width: '100%', fontWeight: 'bold'
                }}
              >
                {analyzing ? 'Consulting Architect...' : '✨ Analyze with AI'}
              </button>
              
              {aiAnalysis && (
                <div style={{ 
                  marginTop: '15px', fontSize: '12px', lineHeight: '1.4', 
                  color: '#d4d4d8', background: '#18181b', padding: '10px',
                  borderRadius: '4px', borderLeft: '3px solid #a855f7',
                  whiteSpace: 'pre-wrap'
                }}>
                  {aiAnalysis}
                </div>
              )}
            </div>
          )}

          <button 
            onClick={handleCloseInspector}
            style={{
              background: '#3f3f46', border: 'none', color: '#fff',
              padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', 
              marginTop: '15px', width: '100%'
            }}
          >
            Close Inspector
          </button>
        </div>
      )}
    </div>
  );
};
