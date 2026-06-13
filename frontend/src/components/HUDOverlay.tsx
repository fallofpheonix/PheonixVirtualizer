import React from 'react';
import { ProcessedNode } from './DependencyGraph3DTypes';

interface HUDOverlayProps {
  selectedNode: ProcessedNode | null;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  onSearch: (e: React.FormEvent) => void;
  filters: Record<string, boolean>;
  setFilters: React.Dispatch<React.SetStateAction<Record<string, boolean>>>;
  onCloseInspector: () => void;
  onAnalyzeAI: (id: string) => void;
  analyzing: boolean;
  aiAnalysis: string | null;
  formatDate: (ts: number | null) => string;
  isDeadCode: (ts: number | null) => boolean;
  getNodeColor: (status: string, kind: string) => string;
}

export const HUDOverlay: React.FC<HUDOverlayProps> = ({
  selectedNode, searchQuery, setSearchQuery, onSearch, filters, setFilters,
  onCloseInspector, onAnalyzeAI, analyzing, aiAnalysis, formatDate, isDeadCode, getNodeColor
}) => {
  return (
    <>
      {/* SEARCH HUD */}
      <div style={{ position: 'absolute', top: '80px', left: '15px', zIndex: 10, width: '280px' }}>
        <form onSubmit={onSearch}>
          <input 
            type="text" placeholder="Search nodes (e.g. auth.py)..."
            value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%', background: 'rgba(24, 24, 27, 0.8)', border: '1px solid #27272a',
              borderRadius: '6px', padding: '10px 15px', color: '#fff', outline: 'none', fontFamily: 'monospace'
            }}
          />
        </form>
      </div>

      {/* FILTER LEGEND */}
      <div style={{
        position: 'absolute', bottom: '20px', left: '20px', zIndex: 10,
        background: 'rgba(24, 24, 27, 0.85)', backdropFilter: 'blur(4px)',
        padding: '15px', borderRadius: '8px', border: '1px solid #27272a',
        color: '#f4f4f5', fontFamily: 'monospace', width: '220px'
      }}>
        <div style={{ marginBottom: '10px', fontSize: '12px', color: '#71717a' }}>FILTERS</div>
        {Object.keys(filters).map(f => (
          <label key={f} style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', cursor: 'pointer' }}>
            <input 
              type="checkbox" checked={filters[f]} 
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

      {/* INSPECTOR */}
      {selectedNode && (
        <div style={{
          position: 'absolute', bottom: '20px', right: '20px', 
          background: 'rgba(26, 26, 26, 0.95)', padding: '20px',
          borderRadius: '8px', border: '1px solid #3f3f46',
          color: '#f4f4f5', width: '350px', maxHeight: '80vh', 
          overflowY: 'auto', fontFamily: 'monospace', zIndex: 10
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: getNodeColor(selectedNode.status, selectedNode.kind) }}>{selectedNode.name}</h3>
          <p><strong>Type:</strong> {selectedNode.kind}</p>
          <p><strong>Path:</strong> {selectedNode.path || './'}</p>
          <p><strong>Status:</strong> <span style={{ color: getNodeColor(selectedNode.status, selectedNode.kind) }}>{selectedNode.status}</span></p>
          
          <div style={{ marginTop: '15px', borderTop: '1px solid #3f3f46', paddingTop: '15px', fontSize: '13px' }}>
            <div style={{ marginBottom: '8px', color: '#a1a1aa' }}>GIT_INTELLIGENCE</div>
            <p><strong>Churn:</strong> {selectedNode.metadata?.churn || 0} commits</p>
            <p><strong>Last Author:</strong> {selectedNode.metadata?.last_commit_author || 'N/A'}</p>
            <p><strong>Last Commit:</strong> {formatDate(selectedNode.metadata?.last_commit_date)}</p>
            
            {isDeadCode(selectedNode.metadata?.last_commit_date) && (
              <div style={{ 
                marginTop: '10px', padding: '8px', background: 'rgba(239, 68, 68, 0.1)', 
                border: '1px solid #ef4444', color: '#ef4444', borderRadius: '4px',
                fontSize: '11px', fontWeight: 'bold'
              }}>
                ⚠️ DEAD CODE SENTINEL: Untouched for 180+ days
              </div>
            )}
          </div>

          {(selectedNode.status === 'WARNING' || selectedNode.status === 'BROKEN') && (
            <div style={{ marginTop: '15px', borderTop: '1px solid #3f3f46', paddingTop: '15px' }}>
              <button 
                onClick={() => onAnalyzeAI(selectedNode.id)}
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
            onClick={onCloseInspector}
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
    </>
  );
};
