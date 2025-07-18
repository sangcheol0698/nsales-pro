import React, { useEffect } from 'react'
import { SessionProvider, useSession } from './contexts/SessionContext'
import { Sidebar } from './components/Sidebar'
import './App.css'

function ChatInterface() {
  const { currentSession, loadHistory } = useSession();

  useEffect(() => {
    // Load history when session changes
    if (currentSession) {
      loadHistory(currentSession.id).then(history => {
        if (history) {
          console.log('Loaded history for session:', currentSession.id, history);
          // Here you would update your chat messages state
        }
      });
    }
  }, [currentSession, loadHistory]);

  return (
    <div style={{ display: 'flex', height: '100vh' }}>
      <Sidebar />
      <div style={{ flex: 1, padding: '2rem' }}>
        <h1>Chat Application</h1>
        {currentSession ? (
          <div>
            <h2>Current Session: {currentSession.title}</h2>
            <p>Session ID: {currentSession.id}</p>
            <p>Created: {new Date(currentSession.createdAt).toLocaleString()}</p>
            <p>Updated: {new Date(currentSession.updatedAt).toLocaleString()}</p>
            
            <div style={{ marginTop: '2rem', padding: '1rem', backgroundColor: '#f9fafb', borderRadius: '0.5rem' }}>
              <h3>Session Management Features:</h3>
              <ul style={{ marginLeft: '1.5rem' }}>
                <li>Click "새 대화" to create a new session with UUID v4</li>
                <li>Sessions are persisted in localStorage</li>
                <li>Current session ID is maintained in React Context and localStorage</li>
                <li>Click on any session in the sidebar to switch</li>
                <li>Use the edit button to rename sessions</li>
                <li>Use the delete button to remove sessions</li>
                <li>History is loaded via API when switching sessions</li>
              </ul>
            </div>
          </div>
        ) : (
          <p>No session selected</p>
        )}
      </div>
    </div>
  );
}

function App() {
  return (
    <SessionProvider>
      <ChatInterface />
    </SessionProvider>
  )
}

export default App
