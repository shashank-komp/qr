import { useEffect, useState } from "react";
import { createSession } from "../services/api";
import { connectSocket, joinSession, onFileUploaded } from "../services/socket";
import { QRCodeCanvas } from "qrcode.react";

export default function QRUpload() {
  const [loading, setLoading] = useState(true);
  const [sessionData, setSessionData] = useState(null);
  const [fileData, setFileData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      setLoading(true);
      const data = await createSession();
      setSessionData(data);

      // Connect mock socket
      connectSocket();
      joinSession(data.sessionId);

      onFileUploaded((fileInfo) => {
        setFileData(fileInfo);
      });

    } catch (err) {
      setError("Failed to create session.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container vh-100 d-flex justify-content-center align-items-center">
      <div className="card shadow p-4 text-center" style={{ width: "400px" }}>

        <h4 className="mb-4">Upload from QR</h4>

        {loading && (
          <>
            <div className="spinner-border text-primary mb-3" role="status" />
            <p>Creating secure session...</p>
          </>
        )}

        {error && (
          <div className="alert alert-danger">{error}</div>
        )}

        {!loading && sessionData && !fileData && (
          <>
           <QRCodeCanvas
            value={sessionData.uploadUrl}
            size={200}
           />
            <p className="mt-3 text-muted">
              Scan this QR code from your phone to upload a file.
            </p>
            <div className="spinner-border spinner-border-sm text-secondary mt-2" />
            <p className="text-muted mt-2">Waiting for file...</p>
          </>
        )}

        {fileData && (
          <>
            <div className="alert alert-success">
              File Received Successfully 🎉
            </div>

            <p><strong>File Name:</strong> {fileData.fileName}</p>

            <button className="btn btn-primary mt-3">
              Download File
            </button>
          </>
        )}

      </div>
    </div>
  );
}