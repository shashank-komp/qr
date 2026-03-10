import { useState } from "react";
import { connectSocket, joinSession, onFileUploaded } from "../services/socket";
import { createSession } from "../services/api";

export default function QRUpload() {
  const [qrCode, setQrCode] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);

  const generateQR = async () => {
    try {
      const data = await createSession();

      setSessionId(data.session_id);
      setQrCode(data.qr_code);

      connectSocket(data.session_id);
      joinSession(data.session_id);

      onFileUploaded((file) => {
        setFiles((prev) => [...prev, file]);
      });

      setError(null);
    } catch {
      setError("Failed to generate QR code. Please try again.");
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <h2>QR Upload</h2>

      <button onClick={generateQR}>
        Generate QR
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "10px" }}>
          {error}
        </p>
      )}

      {qrCode && (
        <div style={{ marginTop: "30px" }}>
          <img
            src={`data:image/png;base64,${qrCode}`}
            alt="QR Code"
            width="300"
          />

          <p>Session ID: {sessionId}</p>
        </div>
      )}

      {files.length > 0 && (
        <div style={{ marginTop: "20px" }}>
          <h3>Uploaded Files</h3>

          {files.map((file, index) => (
            <div key={index} style={{ marginTop: "10px", wordBreak: "break-all" }}>
              {file.location}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}