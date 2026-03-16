import React from "react";

export default function RoomFull() {
    return (
        <div className="container vh-100 d-flex justify-content-center align-items-center">
            <div className="card shadow p-4 text-center" style={{ width: "420px", borderColor: "red" }}>
                <h4 className="text-danger mb-3">QR Already Scanned</h4>
                <p className="text-muted">
                    This QR code has already been used by another device. Please generate a new QR code on your PC.
                </p>
            </div>
        </div>
    );
}
