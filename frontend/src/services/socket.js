// MOCK WebSocket simulation

let listeners = {};

export const connectSocket = () => {
  console.log("Mock socket connected");
};

export const joinSession = (sessionId) => {
  console.log("Joined session:", sessionId);

  // Simulate file upload after 5 seconds
  setTimeout(() => {
    if (listeners["file_uploaded"]) {
      listeners["file_uploaded"]({
        fileName: "example.pdf",
        downloadUrl: "#",
      });
    }
  }, 5000);
};

export const onFileUploaded = (callback) => {
  listeners["file_uploaded"] = callback;
};