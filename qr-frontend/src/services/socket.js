let socket = null;
let fileUploadedListener = null;
let rejectListener = null;
let connectionStatusListener = null;

export const connectSocket = (sessionId, onReject) => {
  const wsBase = process.env.REACT_APP_WS_URL;
  const wsUrl = `${wsBase}/${sessionId}/`;

  if (socket) {
    console.log("Closing existing socket before connecting to new session...");
    closeSocket();
  }

  if (onReject) rejectListener = onReject;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("WebSocket connected:", wsUrl);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log("[WebSocket MESSAGE] Received:", data);

      if (data.status === "uploaded") {
        const file = {
          fileName: data.file_name,
          location: data.file_url
        };
        console.log("[WebSocket] File notification valid, triggering listener...");

        if (fileUploadedListener) {
          fileUploadedListener(file);
        }
      }

      // Proactive redirection on error messages (check type, not code)
      if (data.type === "ROOM_FULL_STATUS" && rejectListener) {
        console.log(`[WebSocket] Room is full, triggering rejection listener...`);
        rejectListener(4003);
      }
      if (data.type === "INVALID_QR_STATUS" && rejectListener) {
        console.log(`[WebSocket] Invalid/expired QR, triggering rejection listener...`);
        rejectListener(4004);
      }

      // Handle connection status updates (e.g., "phone joined")
      if (data.type === "CONNECTION_STATUS" && connectionStatusListener) {
        console.log("[WebSocket] Connection status update:", data.status);
        connectionStatusListener(data.status);
      }

    } catch (err) {
      console.error("Invalid WS message", err);
    }
  };

  socket.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  socket.onclose = (event) => {
    console.log("WebSocket disconnected", event.code);
    if ((event.code === 4003 || event.code === 4004) && rejectListener) {
      rejectListener(event.code);
    }
  };
};

export const joinSession = (sessionId) => {
  console.log("Joined session:", sessionId);
};

export const onFileUploaded = (callback) => {
  fileUploadedListener = callback;
};

export const onConnectionStatus = (callback) => {
  connectionStatusListener = callback;
};

export const closeSocket = () => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close();
  }
};