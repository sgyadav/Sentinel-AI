let socket = null;
const subscribers = new Set();

function getWebSocketUrl() {
  const configuredUrl = import.meta.env.VITE_WS_URL;

  if (configuredUrl) {
    if (configuredUrl.startsWith("ws://") || configuredUrl.startsWith("wss://")) {
      return configuredUrl;
    }

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}${configuredUrl}`;
  }

  const apiUrl = new URL(
    import.meta.env.VITE_API_URL || "https://sentinel-ai-fz5u.onrender.com",
    window.location.origin,
  );
  apiUrl.protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
  apiUrl.pathname = "/ws";
  apiUrl.search = "";
  apiUrl.hash = "";

  return apiUrl.toString();
}

export function connectWebSocket(onMessage) {
  subscribers.add(onMessage);

  if (!socket || socket.readyState === WebSocket.CLOSED) {
    const token = localStorage.getItem("token");
    const protocols = token ? [`bearer.${token}`, "sentinel-auth"] : ["sentinel-auth"];
    socket = new WebSocket(getWebSocketUrl(), protocols);

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
