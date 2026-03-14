import { useEffect, useRef, useCallback, useState } from 'react';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

export function useWebSocket({ onMessage, enabled = true }) {
  const ws = useRef(null);
  const [status, setStatus] = useState('disconnected');
  const reconnectTimer = useRef(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    const token = localStorage.getItem('access_token');
    if (!token || !enabled) return;

    setStatus('connecting');
    const socket = new WebSocket(`${WS_URL}/ws/chat/?token=${token}`);
    ws.current = socket;

    socket.onopen = () => {
      if (mountedRef.current) setStatus('connected');
      clearTimeout(reconnectTimer.current);
    };

    socket.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (onMessage) onMessage(data);
      } catch {}
    };

    socket.onclose = () => {
      if (mountedRef.current) {
        setStatus('disconnected');
        reconnectTimer.current = setTimeout(connect, 3000);
      }
    };

    socket.onerror = () => {
      socket.close();
    };
  }, [enabled, onMessage]);

  useEffect(() => {
    mountedRef.current = true;
    if (enabled) connect();
    return () => {
      mountedRef.current = false;
      clearTimeout(reconnectTimer.current);
      if (ws.current) ws.current.close();
    };
  }, [connect, enabled]);

  const send = useCallback((data) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    }
  }, []);

  return { send, status };
}
