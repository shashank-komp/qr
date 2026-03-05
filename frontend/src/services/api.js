// MOCK API SERVICES (Temporary until backend ready)

export const createSession = async () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const sessionId = Math.random().toString(36).substring(2, 10);

      resolve({
        sessionId,
        uploadUrl: `http://localhost:3000/upload/${sessionId}`,
      });
    }, 1000);
  });
};

export const uploadDirect = async (file) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ message: "File uploaded successfully (mock)." });
    }, 1500);
  });
};

export const uploadViaSession = async (sessionId, file) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ message: "File sent to PC (mock)." });
    }, 1500);
  });
};