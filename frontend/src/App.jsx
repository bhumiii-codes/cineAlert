import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import CreateAlert from "./pages/CreateAlert";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/create" element={<CreateAlert />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}