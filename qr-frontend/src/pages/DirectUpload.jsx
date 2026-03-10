import { useState } from "react";

export default function DirectUpload() {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleUpload = () => {
    if (!file) {
      setMessage("Please select a file.");
      return;
    }

    setMessage("Direct upload is not implemented in backend yet.");
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
        >
          Upload
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