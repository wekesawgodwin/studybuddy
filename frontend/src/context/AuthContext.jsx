// frontend/src/context/AuthContext.jsx

import { createContext, useContext, useState, useEffect } from "react";
import { getMe } from "../api/auth";

// Create the context object.
// The default value (null) is only used when a component renders
// outside of AuthProvider — which should never happen in our app.
const AuthContext = createContext(null);

/**
 * AuthProvider wraps the entire application and makes auth state
 * available to every component via useAuth().
 *
 * State managed here:
 * - token:   the JWT string (null if not logged in)
 * - user:    the current user object from GET /auth/me (null if not loaded)
 * - loading: true while we are verifying an existing stored token on app load
 */
export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  // loading is true during the initial token verification on app load.
  // We start as true so the app does not flash the login page before
  // checking if the user is already logged in from a previous session.
  const [loading, setLoading] = useState(true);

  // On app load: check if a token is already stored in localStorage.
  // If it is, verify it by fetching /auth/me.
  // If the token is invalid (expired, tampered), clear it and show login.
  useEffect(() => {
    const storedToken = localStorage.getItem("studybuddy_token");

    if (!storedToken) {
      // No stored token — user is not logged in
      setLoading(false);
      return;
    }

    // Verify the stored token is still valid
    getMe(storedToken)
      .then((userData) => {
        setToken(storedToken);
        setUser(userData);
      })
      .catch(() => {
        // Token is invalid or expired — clear it
        localStorage.removeItem("studybuddy_token");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  /**
   * Called after successful OTP verification.
   * Stores the JWT and loads the user profile.
   */
  const login = async (newToken) => {
    localStorage.setItem("studybuddy_token", newToken);
    setToken(newToken);

    // Fetch the user profile immediately so components have it available
    const userData = await getMe(newToken);
    setUser(userData);
  };

  /**
   * Clears all auth state and removes the stored token.
   * Called when the user clicks "Log out".
   */
  const logout = () => {
    localStorage.removeItem("studybuddy_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ token, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * useAuth is the custom hook for reading auth state in any component.
 *
 * Usage:
 *   const { token, user, login, logout } = useAuth();
 */
export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside <AuthProvider>");
  }

  return context;
}