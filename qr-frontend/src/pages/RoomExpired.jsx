import React from "react";
import { Link } from "react-router-dom";

export default function RoomExpired() {
    return (
        <div className="container vh-100 d-flex justify-content-center align-items-center">
            <div className="card shadow p-4 text-center" style={{ width: "420px", borderColor: "#6c757d" }}>
                <div className="mb-3">
                    <span style={{ fontSize: "3rem" }}>⏰</span>
                </div>
                <h4 className="text-secondary mb-3">QR Code Expired</h4>
                <p className="text-muted">
                    This QR code is no longer valid or has expired. 
                    Please refresh the page on your computer to generate a new one.
                </p>
                <Link to="/" className="btn btn-outline-secondary mt-2">
                    Back to Home
                </Link>
            </div>
        </div>
    );
}
