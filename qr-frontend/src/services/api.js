import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL;

export const createSession = async () => {
  const response = await axios.get(`${API_BASE}/generate_qr/`);
  return response.data;
};

export const uploadViaSession = async (sessionId, file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    `${API_BASE}/mobile_upload/${sessionId}/`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};