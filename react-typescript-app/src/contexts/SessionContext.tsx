import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Session, SessionHistory } from '../types/session';
import {
  generateNewSession,
  getAllSessions,
  addSession,
  updateSession,
  deleteSession,
  getCurrentSessionId,
  setCurrentSessionId,
  loadHistory as loadSessionHistory,
} from '../utils/sessionUtils';

interface SessionContextType {
  sessions: Session[];
  currentSessionId: string | null;
  currentSession: Session | null;
  createNewSession: () => void;
  selectSession: (sessionId: string) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  removeSession: (sessionId: string) => void;
  loadHistory: (sessionId: string) => Promise<SessionHistory | null>;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

export const useSession = () => {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
};

interface SessionProviderProps {
  children: React.ReactNode;
}

export const SessionProvider: React.FC<SessionProviderProps> = ({ children }) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentSessionId, setCurrentSessionIdState] = useState<string | null>(null);

  // Load sessions and current session ID on mount
  useEffect(() => {
    const loadedSessions = getAllSessions();
    setSessions(loadedSessions);

    const savedSessionId = getCurrentSessionId();
    if (savedSessionId && loadedSessions.some(s => s.id === savedSessionId)) {
      setCurrentSessionIdState(savedSessionId);
    } else if (loadedSessions.length === 0) {
      // Create a new session if none exist
      const newSession = generateNewSession();
      addSession(newSession);
      setSessions([newSession]);
      setCurrentSessionIdState(newSession.id);
      setCurrentSessionId(newSession.id);
    } else {
      // Select the most recent session
      setCurrentSessionIdState(loadedSessions[0].id);
      setCurrentSessionId(loadedSessions[0].id);
    }
  }, []);

  const currentSession = sessions.find(s => s.id === currentSessionId) || null;

  const createNewSession = useCallback(() => {
    const newSession = generateNewSession();
    addSession(newSession);
    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionIdState(newSession.id);
    setCurrentSessionId(newSession.id);
  }, []);

  const selectSession = useCallback((sessionId: string) => {
    if (sessions.some(s => s.id === sessionId)) {
      setCurrentSessionIdState(sessionId);
      setCurrentSessionId(sessionId);
    }
  }, [sessions]);

  const updateSessionTitle = useCallback((sessionId: string, title: string) => {
    updateSession(sessionId, { title });
    setSessions(prev => 
      prev.map(s => s.id === sessionId ? { ...s, title, updatedAt: new Date().toISOString() } : s)
    );
  }, []);

  const removeSession = useCallback((sessionId: string) => {
    deleteSession(sessionId);
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    
    // If the deleted session was current, select another
    if (currentSessionId === sessionId) {
      const remainingSessions = sessions.filter(s => s.id !== sessionId);
      if (remainingSessions.length > 0) {
        const newCurrentId = remainingSessions[0].id;
        setCurrentSessionIdState(newCurrentId);
        setCurrentSessionId(newCurrentId);
      } else {
        // Create a new session if all were deleted
        createNewSession();
      }
    }
  }, [currentSessionId, sessions, createNewSession]);

  const loadHistory = useCallback(async (sessionId: string) => {
    return await loadSessionHistory(sessionId);
  }, []);

  const value: SessionContextType = {
    sessions,
    currentSessionId,
    currentSession,
    createNewSession,
    selectSession,
    updateSessionTitle,
    removeSession,
    loadHistory,
  };

  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
};
