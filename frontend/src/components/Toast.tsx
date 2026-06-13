import React, { useState, useEffect, useCallback } from 'react';

export interface ToastMessage {
  id: string;
  message: string;
  type: 'info' | 'error' | 'warning';
}

export const useToasts = () => {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback((message: string, type: 'info' | 'error' | 'warning' = 'info') => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  }, []);

  return { toasts, addToast };
};

export const ToastContainer: React.FC<{ toasts: ToastMessage[] }> = ({ toasts }) => {
  return (
    <div style={{
      position: 'absolute', bottom: '20px', left: '50%', transform: 'translateX(-50%)',
      zIndex: 100, display: 'flex', flexDirection: 'column', alignItems: 'center',
      pointerEvents: 'none'
    }}>
      {toasts.map(t => (
        <div key={t.id} style={{
          background: t.type === 'error' ? '#ef4444' : (t.type === 'warning' ? '#f59e0b' : '#3b82f6'),
          color: '#fff', padding: '12px 24px', borderRadius: '4px', marginBottom: '10px',
          boxShadow: '0 4px 6px rgba(0,0,0,0.3)', fontFamily: 'monospace',
          fontSize: '14px', fontWeight: 'bold', animation: 'slideUp 0.3s ease-out'
        }}>
          {t.message}
        </div>
      ))}
      <style>{`
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
};
