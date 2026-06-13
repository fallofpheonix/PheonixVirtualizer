import React from 'react';

interface Snapshot {
  timestamp: string;
  violation_count: number;
  cycle_count: number;
  avg_churn: number;
}

interface TrendDashboardProps {
  snapshots: Snapshot[];
  onClose: () => void;
}

export const TrendDashboard: React.FC<TrendDashboardProps> = ({ snapshots, onClose }) => {
  const width = 600;
  const height = 300;
  const padding = 40;

  const renderLine = (data: number[], color: string) => {
    if (data.length < 2) return null;
    const max = Math.max(...data, 1);
    const points = data.map((val, i) => {
      const x = padding + (i / (data.length - 1)) * (width - 2 * padding);
      const y = (height - padding) - (val / max) * (height - 2 * padding);
      return `${x},${y}`;
    }).join(' ');

    return <polyline fill="none" stroke={color} strokeWidth="3" points={points} />;
  };

  return (
    <div style={{
      position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
      zIndex: 200, width: `${width}px`, background: 'rgba(24, 24, 27, 0.95)',
      backdropFilter: 'blur(10px)', padding: '30px', borderRadius: '12px',
      border: '1px solid #3f3f46', color: '#f4f4f5', fontFamily: 'monospace'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', color: '#a855f7' }}>ARCHITECTURAL_HEALTH_TRENDS</h2>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#71717a', cursor: 'pointer' }}>[CLOSE]</button>
      </div>

      <div style={{ display: 'flex', gap: '20px', marginBottom: '20px', fontSize: '12px' }}>
        <div style={{ color: '#ef4444' }}>● VIOLATIONS</div>
        <div style={{ color: '#eab308' }}>● CYCLES</div>
        <div style={{ color: '#3b82f6' }}>● AVG_CHURN</div>
      </div>

      <svg width={width - 60} height={height} style={{ overflow: 'visible' }}>
        {/* Axes */}
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#3f3f46" />
        <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#3f3f46" />

        {renderLine(snapshots.map(s => s.violation_count), '#ef4444')}
        {renderLine(snapshots.map(s => s.cycle_count), '#eab308')}
        {renderLine(snapshots.map(s => s.avg_churn), '#3b82f6')}
      </svg>

      <div style={{ marginTop: '20px', fontSize: '11px', color: '#71717a', textAlign: 'center' }}>
        {snapshots.length} Snapshots recorded since {snapshots[0]?.timestamp ? new Date(snapshots[0].timestamp).toLocaleDateString() : 'N/A'}
      </div>
    </div>
  );
};
