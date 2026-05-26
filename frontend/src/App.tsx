import React, { useState, useEffect } from 'react';
import { DependencyGraph3D } from './components/DependencyGraph3D';

function App() {
  const [graphData, setGraphData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 1. Initial Load from API
    fetch('/api/job/latest/macro')
      .then(res => res.json())
      .then(data => {
        setGraphData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error loading graph:", err);
        fetch('/dependency_graph.json')
          .then(res => res.json())
          .then(data => {
            setGraphData(data);
            setLoading(false);
          });
      });

    // 2. Setup WebSocket for Live Updates
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      if (message.type === 'GRAPH_UPDATE') {
        console.log("Received live graph update from server");
        setGraphData(message.data);
      }
    };

    return () => ws.close();
  }, []);

  if (loading) {
    return (
      <div style={{
        background: '#18181b', color: '#a1a1aa', height: '100vh',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: 'monospace', fontSize: '18px'
      }}>
        [PheonixVirtualizer] Loading local dependency workspace map...
      </div>
    );
  }

  return (
    <div style={{ background: '#111', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Header Metric Bar Layer */}
      <div style={{
        position: 'absolute', top: '15px', left: '15px', zIndex: 10,
        background: 'rgba(24, 24, 27, 0.85)', backdropFilter: 'blur(4px)',
        padding: '12px 20px', borderRadius: '6px', border: '1px solid #27272a',
        color: '#f4f4f5', fontFamily: 'monospace'
      }}>
        <span style={{ color: '#a855f7', fontWeight: 'bold' }}>PHEONIX_VIRTUALIZER</span>
        <div style={{ fontSize: '12px', color: '#71717a', marginTop: '4px' }}>
          Nodes: {graphData.nodes?.length} | Connections: {graphData.edges?.length}
        </div>
      </div>

      <DependencyGraph3D data={graphData} />
    </div>
  );
}

export default App;
