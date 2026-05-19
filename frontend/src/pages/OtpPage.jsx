// frontend/src/pages/OtpPage.jsx

import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { verifyOtp, requestOtp } from "../api/auth";
import { useAuth } from "../context/AuthContext";

/**
 * OtpPage — Step 2 of the passwordless login flow.
 *
 * The user enters the 6-digit code from their email.
 * We call POST /auth/verify-otp.
 * On success we store the JWT and navigate to the dashboard.
 *
 * We also provide a "Resend code" button in case the email was delayed.
 */
export default function OtpPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();

  // The email was passed here via navigate() in LoginPage.
  // If the user navigates directly to /verify-otp without an email,
  // redirect them back to login.
  const email = location.state?.email;

  if (!email) {
    navigate("/login");
    return null;
  }

  // Form state — the 6-digit code the user types
  const [otp, setOtp] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resendLoading, setResendLoading] = useState(false);
  const [resendMessage, setResendMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Verify the OTP — the API returns { access_token, token_type }
      const { access_token } = await verifyOtp(email, otp);

      // Store the token and load the user profile
      await login(access_token);

      // Navigate to the dashboard
      navigate("/dashboard");

    } catch (err) {
      setError(err.message);
      // Clear the OTP input so the user can try again cleanly
      setOtp("");
    } finally {
      setLoading(false);
    }
  };

  /**
   * Resends a new OTP to the same email.
   * The backend invalidates the old OTP and generates a fresh one.
   */
  const handleResend = async () => {
    setResendMessage(null);
    setError(null);
    setResendLoading(true);

    try {
      await requestOtp(email);
      setResendMessage("A new code has been sent to your email.");
      setOtp("");     // clear the old code from the input
    } catch (err) {
      setError("Failed to resend code. Please try again.");
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>Check your email</h1>
        <p style={styles.subtitle}>
          We sent a 6-digit code to <strong>{email}</strong>
        </p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label htmlFor="otp" style={styles.label}>
            Login code
          </label>
          <input
            id="otp"
            type="text"
            inputMode="numeric"     // shows numeric keyboard on mobile
            pattern="\d{6}"         // HTML validation: exactly 6 digits
            maxLength={6}
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="000000"
            required
            disabled={loading}
            style={styles.otpInput}
            autoComplete="one-time-code"  // enables SMS/email OTP autofill on mobile
          />

          {error && <p style={styles.error}>{error}</p>}
          {resendMessage && <p style={styles.success}>{resendMessage}</p>}

          <button type="submit" disabled={loading || otp.length !== 6} style={styles.button}>
            {loading ? "Verifying..." : "Verify code"}
          </button>
        </form>

        {/* Resend option */}
        <div style={styles.resendContainer}>
          <span style={styles.resendText}>Didn't receive the code? </span>
          <button
            onClick={handleResend}
            disabled={resendLoading}
            style={styles.resendButton}
          >
            {resendLoading ? "Sending..." : "Resend code"}
          </button>
        </div>

        {/* Back link */}
        <button onClick={() => navigate("/login")} style={styles.backButton}>
          ← Use a different email
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f9fafb",
  },
  card: {
    background: "#fff",
    padding: "40px",
    borderRadius: "12px",
    boxShadow: "0 2px 16px rgba(0,0,0,0.08)",
    width: "100%",
    maxWidth: "400px",
  },
  title: { margin: 0, fontSize: "24px", fontWeight: "700" },
  subtitle: { color: "#666", marginTop: "8px", marginBottom: "24px" },
  form: { display: "flex", flexDirection: "column", gap: "12px" },
  label: { fontWeight: "600", fontSize: "14px" },
  otpInput: {
    padding: "16px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    fontSize: "32px",
    letterSpacing: "12px",
    textAlign: "center",
    fontWeight: "700",
  },
  button: {
    padding: "14px",
    background: "#4f46e5",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "600",
    cursor: "pointer",
    marginTop: "8px",
  },
  error: { color: "#dc2626", fontSize: "14px", margin: 0 },
  success: { color: "#16a34a", fontSize: "14px", margin: 0 },
  resendContainer: { marginTop: "20px", fontSize: "14px" },
  resendText: { color: "#666" },
  resendButton: {
    background: "none",
    border: "none",
    color: "#4f46e5",
    cursor: "pointer",
    fontWeight: "600",
    textDecoration: "underline",
    padding: 0,
  },
  backButton: {
    marginTop: "12px",
    background: "none",
    border: "none",
    color: "#666",
    cursor: "pointer",
    fontSize: "14px",
    padding: 0,
  },
};