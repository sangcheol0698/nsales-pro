import { v4 as uuidv4 } from 'uuid';
import { Session, SessionHistory } from '../types/session';

const SESSION_STORAGE_KEY = 'chat_sessions';
const CURRENT_SESSION_KEY = 'current_session_id';

// Generate a new session with UUID v4
export const generateNewSession = (): Session => {
  const now = new Date().toISOString();
  return {
    id: uuidv4(),
    title: '새 대화',
    createdAt: now,
    updatedAt: now,
  };
};

// Get all sessions from localStorage
export const getAllSessions = (): Session[] => {
  try {
    const sessionsJson = localStorage.getItem(SESSION_STORAGE_KEY);
    return sessionsJson ? JSON.parse(sessionsJson) : [];
  } catch (error) {
    console.error('Error loading sessions:', error);
    return [];
  }
};

// Save sessions to localStorage
export const saveSessions = (sessions: Session[]): void => {
  try {
    localStorage.setItem(SESSION_STORAGE_KEY, JSON.stringify(sessions));
  } catch (error) {
    console.error('Error saving sessions:', error);
  }
};

// Add a new session
export const addSession = (session: Session): void => {
  const sessions = getAllSessions();
  sessions.unshift(session); // Add to beginning
  saveSessions(sessions);
};

// Update a session
export const updateSession = (sessionId: string, updates: Partial<Session>): void => {
  const sessions = getAllSessions();
  const index = sessions.findIndex(s => s.id === sessionId);
  if (index !== -1) {
    sessions[index] = { ...sessions[index], ...updates, updatedAt: new Date().toISOString() };
    saveSessions(sessions);
  }
};

// Delete a session
export const deleteSession = (sessionId: string): void => {
  const sessions = getAllSessions();
  const filtered = sessions.filter(s => s.id !== sessionId);
  saveSessions(filtered);
};

// Get current session ID from localStorage
export const getCurrentSessionId = (): string | null => {
  return localStorage.getItem(CURRENT_SESSION_KEY);
};

// Set current session ID in localStorage
export const setCurrentSessionId = (id: string): void => {
  localStorage.setItem(CURRENT_SESSION_KEY, id);
};

// Load history from API
export const loadHistory = async (id: string): Promise<SessionHistory | null> => {
  try {
    const response = await fetch(`/api/v1/history/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to load history: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error loading history:', error);
    return null;
  }
};
