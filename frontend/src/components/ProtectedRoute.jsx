// frontend/src/components/ProtectedRoute.jsx

import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * ProtectedRoute wraps any route that requires the user to be logged in.
 *
 * While the app is checking if a stored token is valid (loading === true),
 * we render nothing to avoid a flash of the login page.
 *
 * If there is no token, we redirect to /login.
 * If there is a token, we render the wrapped page.
 *
 * Usage in App.jsx:
 *   <Route path="/dashboard" element={
 *     <ProtectedRoute><DashboardPage /></ProtectedRoute>
 *   } />
 */
export default function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();

  // Still checking if the stored token is valid — render nothing yet
  if (loading) {
    return null;
  }

  // No token — redirect to login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Token exists — render the protected content
  return children;
}