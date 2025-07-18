import React from 'react';
import { useSession } from '../contexts/SessionContext';

export const Sidebar: React.FC = () => {
  const {
    sessions,
    currentSessionId,
    createNewSession,
    selectSession,
    updateSessionTitle,
    removeSession,
  } = useSession();

  const handleNewChat = () => {
    createNewSession();
  };

  const handleSelectSession = (sessionId: string) => {
    selectSession(sessionId);
  };

  const handleDeleteSession = (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    removeSession(sessionId);
  };

  const handleRenameSession = (sessionId: string) => {
    const currentSession = sessions.find(s => s.id === sessionId);
    if (currentSession) {
      const newTitle = prompt('Enter new title:', currentSession.title);
      if (newTitle && newTitle.trim()) {
        updateSessionTitle(sessionId, newTitle.trim());
      }
    }
  };

  return (
    <div style={{
      width: '250px',
      height: '100vh',
      backgroundColor: '#f3f4f6',
      padding: '1rem',
      boxSizing: 'border-box',
      overflowY: 'auto',
    }}>
      <button
        onClick={handleNewChat}
        style={{
          width: '100%',
          padding: '0.75rem',
          backgroundColor: '#3b82f6',
          color: 'white',
          border: 'none',
          borderRadius: '0.375rem',
          cursor: 'pointer',
          fontSize: '1rem',
          marginBottom: '1rem',
        }}
      >
        새 대화
      </button>

      <div style={{ marginTop: '1rem' }}>
        <h3 style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem' }}>
          대화 목록
        </h3>
        {sessions.map((session) => (
          <div
            key={session.id}
            onClick={() => handleSelectSession(session.id)}
            style={{
              padding: '0.5rem',
              marginBottom: '0.25rem',
              backgroundColor: currentSessionId === session.id ? '#e5e7eb' : 'transparent',
              borderRadius: '0.375rem',
              cursor: 'pointer',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <div
                style={{
                  fontSize: '0.875rem',
                  whiteSpace: 'nowrap',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                }}
              >
                {session.title}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                {new Date(session.updatedAt).toLocaleDateString()}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '0.25rem' }}>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleRenameSession(session.id);
                }}
                style={{
                  padding: '0.25rem',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                }}
                title="Rename"
              >
                ✏️
              </button>
              <button
                onClick={(e) => handleDeleteSession(e, session.id)}
                style={{
                  padding: '0.25rem',
                  backgroundColor: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  fontSize: '0.75rem',
                }}
                title="Delete"
              >
                🗑️
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
