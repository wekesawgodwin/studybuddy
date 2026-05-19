// frontend/src/pages/LoginPage.jsx

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { requestOtp } from "../api/auth";

/**
 * LoginPage — Step 1 of the passwordless login flow.
 *
 * The user enters their email and submits the form.
 * We call POST /auth/request-otp.
 * On success we navigate to /verify-otp and pass the email along
 * via React Router's location state so OtpPage knows which email to submit.
 */
export default function LoginPage() {
  const navigate = useNavigate();

  // Form state
  const [email, setEmail] = useState("");

  // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();         // prevent browser from reloading the page
    setError(null);
    setLoading(true);

    try {
      await requestOtp(email);

      // Navigate to the OTP entry page.
      // We pass the email via state so OtpPage can use it without the user
      // having to type it again.
      navigate("/verify-otp", { state: { email } });

    } catch (err) {
      // Display the error message returned from the API
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>StudyBuddy</h1>
        <p style={styles.subtitle}>Enter your email to receive a login code</p>

        <form onSubmit={handleSubmit} style={styles.form}>
          <label htmlFor="email" style={styles.label}>
            Email address
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            disabled={loading}
            style={styles.input}
          />

          {/* Show error message if request failed */}
          {error && <p style={styles.error}>{error}</p>}

          <button type="submit" disabled={loading} style={styles.button}>
            {loading ? "Sending code..." : "Send login code"}
          </button>
        </form>
      </div>
    </div>
  );
}

// Inline styles — replace with your CSS framework or stylesheet as needed
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
  input: {
    padding: "12px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    fontSize: "16px",
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
};