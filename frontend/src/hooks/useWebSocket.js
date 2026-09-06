import { useEffect, useRef, useState, useCallback } from 'react';

const RECONNECT_INTERVAL = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

export const useWebSocket = (url, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  const ws = useRef(null);
  const reconnectAttempts = useRef(0);
  const isIntentionalClose = useRef(false);
  
  const onMessageRef = useRef(onMessage);

  useEffect(() => {
    onMessageRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    // Determine the base WebSocket URL based on API URL or current origin
    const token = localStorage.getItem('cg_access_token');
    if (!token) return;

    let wsUrl = url;
    if (!wsUrl.startsWith('ws')) {
      const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const wsBase = baseUrl.replace(/^http/, 'ws');
      wsUrl = `${wsBase}${url}`;
    }

    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      // Authenticate with JWT as the first message
      ws.current.send(JSON.stringify({ token }));
    };

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status === 'authenticated') {
          setIsConnected(true);
          reconnectAttempts.current = 0;
          setError(null);
        } else if (onMessageRef.current) {
          onMessageRef.current(data);
        }
      } catch (err) {
        console.error('WebSocket message parsing error', err);
      }
    };

    ws.current.onerror = (e) => {
      setError('WebSocket encountered an error.');
    };

    ws.current.onclose = (event) => {
      setIsConnected(false);
      
      // 1008 indicates policy violation (like invalid token)
      if (event.code === 1008) {
        setError('WebSocket authentication failed. Please login again.');
        return;
      }
      
      if (!isIntentionalClose.current && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
        setTimeout(() => {
          reconnectAttempts.current += 1;
          connect();
        }, RECONNECT_INTERVAL);
      } else if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
        setError('Maximum WebSocket reconnection attempts reached.');
      }
    };
  }, [url]); // Removed onMessage to prevent reconnect loops on re-renders

  const disconnect = useCallback(() => {
    isIntentionalClose.current = true;
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return { isConnected, error };
};
