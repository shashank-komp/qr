import { useState } from "react";
import { useParams } from "react-router-dom";
import { uploadViaSession } from "../services/api";

export default function PhoneUpload() {
  const { sessionId } = useParams();

  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      await uploadViaSession(sessionId, file);

      setSuccess(true);
    } catch (err) {
      setError("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container vh-100 d-flex justify-content-center align-items-center">
      <div className="card shadow p-4 text-center" style={{ width: "400px" }}>
        
        {!success ? (
          <>
            <h4 className="mb-3">Send File to PC</h4>

            <p className="text-muted mb-3">
              Session ID: <strong>{sessionId}</strong>
            </p>

            <input
              type="file"
              className="form-control mb-3"
              onChange={(e) => setFile(e.target.files[0])}
            />

            {error && (
              <div className="alert alert-danger py-2">
                {error}
              </div>
            )}

            <button
              className="btn btn-primary w-100"
              onClick={handleUpload}
              disabled={loading}
            >
              {loading ? "Sending..." : "Send to PC"}
            </button>
          </>
        ) : (
          <>
            <div className="alert alert-success">
              File Sent Successfully 🎉
            </div>

            <p className="text-muted">
              You can now return to your PC.
            </p>
            
          </>
        )}

      </div>
    </div>
  );
}