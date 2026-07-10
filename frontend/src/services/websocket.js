let socket = null;
const subscribers = new Set();

function getWebSocketUrl() {
  const configuredUrl = import.meta.env.VITE_WS_URL;
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";

  if (configuredUrl) {
    if (configuredUrl.startsWith("ws://") || configuredUrl.startsWith("wss://")) {
      return configuredUrl;
    }

    return `${protocol}//${window.location.host}${configuredUrl}`;
  }

  return `${protocol}//${window.location.hostname}:8000/ws`;
}

export function connectWebSocket(onMessage) {
  subscribers.add(onMessage);

  if (!socket || socket.readyState === WebSocket.CLOSED) {
    socket = new WebSocket(getWebSocketUrl());

    socket.onopen = () => {
      console.log("WebSocket connected");
      socket.send("connected");
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        subscribers.forEach((subscriber) => subscriber(data));
      } catch (error) {
        console.log("Invalid WebSocket message", error);
      }
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected");
      socket = null;
    };
  }

  return () => closeWebSocket(onMessage);
}

export function closeWebSocket(onMessage) {
  if (onMessage) {
    subscribers.delete(onMessage);
  } else {
    subscribers.clear();
  }

  if (subscribers.size === 0 && socket) {
    socket.close();
    socket = null;
  }
}
