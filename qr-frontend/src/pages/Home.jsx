import { useNavigate } from "react-router-dom";

export default function Home() {
    const navigate = useNavigate();

    return (
        <div className="container vh-100 d-flex flex-column justify-content-center align-items-center">
            <h2 className="mb-4">Upload File</h2>
            <div className="card p-4 shadow" style={{ width: "300px" }}>


                <button className="btn btn-outline-primary " onClick={() => navigate("/qr-upload")}>
                    Upload from QR
                </button>
            </div>
        </div>
    )
}