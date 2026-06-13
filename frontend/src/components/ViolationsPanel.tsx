import React from 'react';
import { NodeStatus } from './DependencyGraph3D';

export interface Violation {
  id: string;
  ruleId: string;
  severity: string;
  message: string;
  sourceNodeIds: string[];
  edgeIds: string[];
  status: string;
  metadata?: any;
}

interface ViolationsPanelProps {
  violations: Violation[];
  onViolationClick: (violation: Violation) => void;
}

export const ViolationsPanel: React.FC<ViolationsPanelProps> = ({ violations, onViolationClick }) => {
  if (!violations.length) return null;

  return (
    <div style={{
      position: 'absolute', top: '80px', right: '15px', zIndex: 10,
      width: '320px', maxHeight: '40vh', overflowY: 'auto',
      background: 'rgba(24, 24, 27, 0.9)', backdropFilter: 'blur(8px)',
      padding: '15px', borderRadius: '8px', border: '1px solid #3f3f46',
      color: '#f4f4f5', fontFamily: 'monospace'
    }}>
      <div style={{ marginBottom: '12px', fontSize: '12px', color: '#71717a', display: 'flex', justifyContent: 'space-between' }}>
        <span>VIOLATIONS</span>
        <span style={{ color: '#ef4444' }}>{violations.length} ACTIVE</span>
      </div>
      
      {violations.map(v => (
        <div 
          key={v.id} 
          onClick={() => onViolationClick(v)}
          style={{
            background: 'rgba(39, 39, 42, 0.6)', padding: '10px',
            borderRadius: '4px', borderLeft: `4px solid ${v.severity === 'high' ? '#ef4444' : '#eab308'}`,
            marginBottom: '8px', cursor: 'pointer', transition: 'background 0.2s'
          }}
          onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(39, 39, 42, 0.9)'}
          onMouseLeave={(e) => e.currentTarget.style.background = 'rgba(39, 39, 42, 0.6)'}
        >
          <div style={{ fontSize: '11px', color: '#a1a1aa', marginBottom: '4px' }}>{v.ruleId}</div>
          <div style={{ fontSize: '12px', lineHeight: '1.4' }}>{v.message}</div>
        </div>
      ))}
    </div>
  );
};
