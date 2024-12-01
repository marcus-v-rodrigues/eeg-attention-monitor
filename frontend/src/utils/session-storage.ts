import { SessionInfo } from '../types/monitoring';

export async function saveSession(sessionData: any): Promise<void> {
  try {
    const response = await fetch('/api/v1/session/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(sessionData),
    });

    if (!response.ok) {
      throw new Error('Failed to save session');
    }
  } catch (error) {
    console.error('Error saving session:', error);
    throw error;
  }
}

export async function loadSession(sessionId: string): Promise<any> {
  try {
    const response = await fetch(`/api/v1/session/load/${sessionId}`);
    if (!response.ok) {
      throw new Error('Failed to load session');
    }
    return response.json();
  } catch (error) {
    console.error('Error loading session:', error);
    throw error;
  }
}

export async function getSessions(): Promise<SessionInfo[]> {
  try {
    const response = await fetch('/api/v1/sessions');
    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching sessions:', error);
    throw error;
  }
}