import { useState, useEffect } from "react";
import { connectSocket, joinSession, onFileUploaded, onConnectionStatus } from "../services/socket";
import { createSession } from "../services/api";

export default function QRUpload() {
  const [qrCode, setQrCode] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [timeLeft, setTimeLeft] = useState(30);
  const [isExpired, setIsExpired] = useState(false);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);
  const [mobileConnected, setMobileConnected] = useState(false);

  const generateQR = async () => {
    try {
      const data = await createSession();

      setSessionId(data.room_id);
      setQrCode(data.qr_code);
      setTimeLeft(30);
      setIsExpired(false);
      setMobileConnected(false); // Reset on new session

      connectSocket(data.room_id);
      joinSession(data.room_id);

      onFileUploaded((file) => {
        setFiles((prev) => [...prev, file]);
      });

      onConnectionStatus((status) => {
        if (status === "mobile_connected") {
          setMobileConnected(true);
        }
      });

      setError(null);
    } catch {
      setError("Failed to generate QR code. Please try again.");
    }
  };

  useEffect(() => {
    if (!qrCode || isExpired) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          console.log("[QRUpload] Timer hit 0! Blurring QR code, but keeping WebSocket connection ACTIVE.");
          clearInterval(timer);
          setIsExpired(true);
          // Removed closeSocket() so the session stays active on the backend!
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [qrCode, isExpired]);

  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <h2>QR Upload</h2>

      <button onClick={generateQR}>
        {isExpired ? "Regenerate QR" : "Generate QR"}
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "10px" }}>
          {error}
        </p>
      )}

      {qrCode && !mobileConnected && (
        <div style={{ marginTop: "30px", position: "relative", display: "inline-block" }}>
          <img
            src={`data:image/png;base64,${qrCode}`}
            alt="QR Code"
            width="300"
            style={{
              filter: isExpired ? "blur(10px)" : "none",
              transition: "filter 0.5s ease-in-out"
            }}
          />
          {isExpired && (
            <div style={{
              position: "absolute", top: "50%", left: "50%",
              transform: "translate(-50%, -50%)", color: "red",
              fontWeight: "bold", backgroundColor: "rgba(255,255,255,0.9)",
              padding: "10px 20px", borderRadius: "8px", border: "2px solid red"
            }}>
              QR Expired
            </div>
          )}

          <p>Session ID: {sessionId}</p>
          {!isExpired && <p style={{ color: "blue", fontWeight: "bold", fontSize: "1.2rem" }}>Expires in: {timeLeft}s</p>}
        </div>
      )}

      {mobileConnected && (
        <div style={{ marginTop: "30px", padding: "20px", border: "2px solid green", borderRadius: "10px", backgroundColor: "#e6ffe6", display: "inline-block" }}>
          <h3 style={{ color: "green" }}>✅ Phone Connected!</h3>
          <p>You can now upload files from your phone.</p>
          <p className="text-muted">Wait for files to appear below...</p>
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