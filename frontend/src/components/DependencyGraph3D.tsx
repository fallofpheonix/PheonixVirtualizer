import React, { useRef, useState, useEffect } from 'react';
import { NodeStatus } from './types';
import { GraphData, ProcessedNode } from './DependencyGraph3DTypes';
import { useGraphData } from './useGraphData';
import { SceneManager } from './SceneManager';
import { HUDOverlay } from './HUDOverlay';
import { ViolationsPanel, Violation } from './ViolationsPanel';
import { ToastContainer, useToasts } from './Toast';

export const DependencyGraph3D: React.FC<{ data: GraphData & { violations?: Violation[] } }> = ({ data }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);
  const [selectedNode, setSelectedNode] = useState<ProcessedNode | null>(null);
  const [hoverNode, setHoverNode] = useState<ProcessedNode | null>(null);
  const [aiAnalysis, setAiAnalysis] = useState<string | null>(null);
  const [analyzing, setAiAnalyzing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<Record<string, boolean>>({
    VERIFIED: true,
    BROKEN: true,
    WARNING: true,
    EXTERNAL_PACKAGE: true
  });

  const { toasts, addToast } = useToasts();
  const lastViolationsCount = useRef(0);

  const processedData = useGraphData(data, filters);

  useEffect(() => {
    const currentViolations = data?.violations || [];
    if (currentViolations.length > lastViolationsCount.current) {
      const newCount = currentViolations.length - lastViolationsCount.current;
      const latest = currentViolations.slice(-newCount);
      latest.forEach(v => {
        addToast(`Sentinel Alert: ${v.message}`, v.severity === 'high' ? 'error' : 'warning');
      });
    }
    lastViolationsCount.current = currentViolations.length;
  }, [data?.violations, addToast]);

  const analyzeWithAI = async (violationId: string) => {
    setAiAnalyzing(true);
    setAiAnalysis(null);
    try {
      const jobId = "default-project"; 
      const response = await fetch(`/api/job/${jobId}/analyze-violation/${violationId}`, {
        method: 'POST',
        headers: { 'X-API-Key': 'dev-key-12345' }
      });
      const resData = await response.json();
      setAiAnalysis(resData.analysis);
    } catch (err) {
      setAiAnalysis("Failed to generate AI analysis.");
    } finally {
      setAiAnalyzing(false);
    }
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

  const handleViolationClick = (violation: Violation) => {
    const nodeId = violation.sourceNodeIds[0];
    const match = processedData.nodes.find(n => n.id === nodeId);
    if (match && graphRef.current) {
      setSelectedNode(match);
      const distance = 120;
      const distRatio = 1 + distance / Math.hypot(match.x || 0, match.y || 0, match.z || 0);
      graphRef.current.cameraPosition(
        { x: (match.x || 0) * distRatio, y: (match.y || 0) * distRatio, z: (match.z || 0) * distRatio },
        match as any,
        1000
      );
    }
  };

  function getNodeColor(status: string | NodeStatus, kind: string): string {
    if (kind === 'PROJECT') return '#a855f7';
    if (kind === 'FOLDER') return '#e2e8f0';
    if (kind === 'EXTERNAL_PACKAGE') return '#3b82f6';
    switch (status) {
      case NodeStatus.VERIFIED: return '#22c55e';
      case NodeStatus.BROKEN: return '#ef4444';
      case NodeStatus.WARNING: return '#eab308';
      default: return '#94a3b8';
    }
  }

  return (
    <div style={{ width: '100%', height: '100vh', position: 'relative', background: '#09090b' }}>
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />

      <SceneManager 
        containerRef={containerRef} graphData={processedData}
        selectedNode={selectedNode} hoverNode={hoverNode}
        onNodeClick={(n: any) => { setSelectedNode(n); setAiAnalysis(null); }}
        onNodeHover={(n: any) => setHoverNode(n)}
        graphRef={graphRef}
      />

      <HUDOverlay 
        selectedNode={selectedNode} searchQuery={searchQuery}
        setSearchQuery={setSearchQuery} onSearch={handleSearch}
        filters={filters} setFilters={setFilters}
        onCloseInspector={() => setSelectedNode(null)}
        onAnalyzeAI={analyzeWithAI} analyzing={analyzing}
        aiAnalysis={aiAnalysis} formatDate={(ts) => ts ? new Date(ts * 1000).toLocaleDateString() : 'Unknown'}
        isDeadCode={(ts) => !!ts && ts < (Date.now() / 1000 - 180 * 24 * 60 * 60)}
        getNodeColor={getNodeColor as any}
      />

      <ViolationsPanel violations={data?.violations || []} onViolationClick={handleViolationClick} />
      <ToastContainer toasts={toasts} />
    </div>
  );
};
