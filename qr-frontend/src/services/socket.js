let socket = null;
let fileUploadedListener = null;
let rejectListener = null;

export const connectSocket = (sessionId, onReject) => {
  const wsBase = process.env.REACT_APP_WS_URL;
  const wsUrl = `${wsBase}/${sessionId}/`;

  if (onReject) rejectListener = onReject;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log("WebSocket connected:", wsUrl);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.status === "uploaded") {
        const file = {
          fileName: data.file_name,
          location: data.file_url
        };

        if (fileUploadedListener) {
          fileUploadedListener(file);
        }
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
    if (event.code === 4003 && rejectListener) {
      rejectListener();
    }
  };
};

export const joinSession = (sessionId) => {
  console.log("Joined session:", sessionId);
};

export const onFileUploaded = (callback) => {
  fileUploadedListener = callback;
};

export const closeSocket = () => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close();
  }
};