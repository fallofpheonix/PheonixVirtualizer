import React, { useEffect, useRef, useState } from 'react';
import ForceGraph3D from '3d-force-graph';

interface GraphData {
  nodes: any[];
  edges: any[];
}

export const DependencyGraph3D: React.FC<{ data: GraphData }> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [analyzing, setAiAnalyzing] = useState(false);

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
    if (!containerRef.current || !data) return;

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
        setAiAnalysis(null);
        const distance = 40;
        const distRatio = 1 + distance / Math.hypot((node as any).x || 0, (node as any).y || 0, (node as any).z || 0);
        Graph.cameraPosition(
          { x: (node as any).x * distRatio, y: (node as any).y * distRatio, z: (node as any).z * distRatio },
          node as any,
          1000
        );
      });

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

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      
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
