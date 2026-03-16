import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { uploadViaSession } from "../services/api";
import { connectSocket, closeSocket } from "../services/socket";

export default function PhoneUpload() {
  const { sessionId } = useParams();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [error, setError] = useState("");
  const [roomFull, setRoomFull] = useState(false);

  useEffect(() => {
    // Establish connection immediately to claim a slot in the room
    connectSocket(sessionId, () => setRoomFull(true));

    return () => {
      closeSocket();
    };
  }, [sessionId]);

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await uploadViaSession(sessionId, file);
      setSuccessMessage(response.message);

    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("Upload failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  if (roomFull) {
    return (
      <div className="container vh-100 d-flex justify-content-center align-items-center">
        <div className="card shadow p-4 text-center" style={{ width: "420px", borderColor: "red" }}>
          <h4 className="text-danger mb-3">QR Already Scanned</h4>
          <p className="text-muted">This QR code has already been used by another device. Please generate a new QR code on your PC.</p>
          <button className="btn btn-outline-danger w-100" onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

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