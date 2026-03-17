import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import DirectUpload from "./pages/DirectUpload";
import QRUpload from "./pages/QRUpload";
import PhoneUpload from "./pages/PhoneUpload";
import RoomFull from "./pages/RoomFull";
import RoomExpired from "./pages/RoomExpired";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/direct-upload" element={<DirectUpload />} />
        <Route path="/qr-upload" element={<QRUpload />} />

        {/* Route used when phone scans QR */}
        <Route path="/qr/mobile_upload/:sessionId" element={<PhoneUpload />} />

        {/* Redirect routes for errors */}
        <Route path="/room-full" element={<RoomFull />} />
        <Route path="/room-expired" element={<RoomExpired />} />

        {/* Optional fallback route */}
        <Route path="/upload/:sessionId" element={<PhoneUpload />} />
      </Routes>
    </Router>
  );
}

export default App;