import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { uploadViaSession } from "../services/api";
import { connectSocket, closeSocket } from "../services/socket";

export default function PhoneUpload() {
  const { sessionId } = useParams();
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    console.log(`[PhoneUpload] Mounting. Attempting to connect WebSocket to session: ${sessionId}`);
    // Establish connection immediately to claim a slot in the room
    connectSocket(sessionId, () => {
      console.log(`[PhoneUpload] Received Room Full (4003) rejection! Redirecting to /room-full`);
      navigate("/room-full");
    });

    return () => {
      console.log(`[PhoneUpload] Unmounting. Closing socket.`);
      closeSocket();
    };
  }, [sessionId, navigate]);

  const handleUpload = async (isRetry = false) => {
    if (!file) {
      setError("Please select a file.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await uploadViaSession(sessionId, file);
      setSuccessMessage(response.message);
      setLoading(false);

    } catch (err) {
      const errorMsg = err.response?.data?.error || "Upload failed.";
      const statusCode = err.response?.status;

      // Auto-retry once if it's the cold-start race condition (403 Forbidden)
      if (statusCode === 403 && !isRetry) {
        console.log("[PhoneUpload] PC not ready (403). Retrying in 1.5s...");
        setError("Establishing connection with PC...");
        setTimeout(() => {
          handleUpload(true);
        }, 1500);
        return;
      }

      setError(errorMsg);
      setLoading(false);
    }
  };

  return (
    <div className="container vh-100 d-flex justify-content-center align-items-center">
      <div className="card shadow p-4 text-center" style={{ width: "420px" }}>
        <h4 className="mb-4">Send File to PC</h4>

        {!successMessage && (
          <>
            <p className="text-muted mb-3">
              Session: <strong>{sessionId}</strong>
            </p>

            <input
              type="file"
              className="form-control mb-3"
              onChange={(e) => setFile(e.target.files[0])}
            />

            {error && (
              <div className="alert alert-danger py-2">{error}</div>
            )}

            <button
              className="btn btn-primary w-100"
              onClick={handleUpload}
              disabled={loading}
            >
              {loading ? "Uploading..." : "Send File"}
            </button>
          </>
        )}

        {successMessage && (
          <>
            <div className="alert alert-success">{successMessage}</div>
            <p className="text-muted">You can now return to your PC.</p>
          </>
        )}
      </div>
    </div>
  );
}