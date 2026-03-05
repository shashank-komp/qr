import { useState } from "react";
import { uploadDirect } from "../services/api";

export default function DirectUpload() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const handleUpload = async () => {
    if (!file) {
      setMessage("Please select a file first.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      await uploadDirect(file);

      setMessage("File uploaded successfully!");
      setFile(null);
    } catch (error) {
      setMessage("Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5" style={{ maxWidth: "500px" }}>
      <h3 className="mb-4">Direct Upload</h3>

      <div className="card p-4 shadow">
        <input
          type="file"
          className="form-control mb-3"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>

        {message && (
          <div className="alert alert-info mt-3">
            {message}
          </div>
        )}
      </div>
    </div>
  );
}