// frontend/src/App.jsx

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import OtpPage from "./pages/OtpPage";

/**
 * Temporary dashboard placeholder — replace with real DashboardPage in Sprint 2.
 */
function Dashboard() {
  const { user, logout } = useAuth();
  return (
    <div style={{ padding: 40 }}>
      <h1>Welcome, {user?.email}</h1>
      <button onClick={logout}>Log out</button>
    </div>
  );
}

// useAuth must be imported here too for the Dashboard placeholder
import { useAuth } from "./context/AuthContext";

export default function App() {
  return (
    /*
     * AuthProvider must wrap BrowserRouter so that ProtectedRoute
     * and all pages can access auth state via useAuth().
     */
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes — accessible without a token */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/verify-otp" element={<OtpPage />} />

          {/* Protected routes — redirect to /login if no token */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}