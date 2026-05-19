// frontend/src/api/auth.js

const BASE_URL = import.meta.env.VITE_API_URL;

/**
 * Requests an OTP for the given email address.
 * Calls POST /auth/request-otp.
 *
 * @param {string} email - the user's email address
 * @returns {Promise<{ message: string }>}
 * @throws {Error} if the request fails
 */
export async function requestOtp(email) {
  const response = await fetch(`${BASE_URL}/auth/request-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!response.ok) {
    // Parse and throw the FastAPI error detail so the UI can display it
    const error = await response.json();
    throw new Error(error.detail || "Failed to send OTP");
  }

  return response.json();
}

/**
 * Verifies the OTP submitted by the user.
 * Calls POST /auth/verify-otp.
 *
 * @param {string} email - the user's email address
 * @param {string} otp   - the 6-digit code from the user's inbox
 * @returns {Promise<{ access_token: string, token_type: string }>}
 * @throws {Error} if the OTP is invalid or expired
 */
export async function verifyOtp(email, otp) {
  const response = await fetch(`${BASE_URL}/auth/verify-otp`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, otp }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Invalid code. Please try again.");
  }

  return response.json();
}

/**
 * Fetches the current authenticated user's profile.
 * Calls GET /auth/me.
 *
 * @param {string} token - the JWT stored in AuthContext
 * @returns {Promise<{ id: string, email: string, is_active: boolean }>}
 */
export async function getMe(token) {
  const response = await fetch(`${BASE_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch user profile");
  }

  return response.json();
}