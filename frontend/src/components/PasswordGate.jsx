import React, { useState } from "react";
import { setSitePassword, apiBase } from "../lib/api";

export default function PasswordGate({ onAuthenticated }) {
  const [passwordInput, setPasswordInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!passwordInput.trim()) return;

    setLoading(true);
    setErrorMsg("");

    // Set the password in memory temporarily
    setSitePassword(passwordInput);

    try {
      // Test the credentials against the backend health endpoint
      const resp = await fetch(`${apiBase}/health`);
      if (resp.ok) {
        // Correct password: store in sessionStorage to persist across tab reloads
        sessionStorage.setItem("site_access_password", passwordInput);
        onAuthenticated();
      } else {
        setErrorMsg("Incorrect access password. Please try again.");
        setSitePassword(""); // Clear the invalid password
      }
    } catch (err) {
      setErrorMsg("Unable to reach the backend server. Please verify it is running.");
      setSitePassword("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="password-gate-container">
      <div className="password-gate-card">
        <div className="password-gate-logo">🔒</div>
        <h1 className="password-gate-title">UPRVUNL CODSP</h1>
        <p className="password-gate-subtitle">
          Decision Support Platform
          <br />
          <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Temporary Site Access Gate</span>
        </p>

        {loading ? (
          <div className="password-gate-loading-spinner" />
        ) : (
          <form className="password-gate-form" onSubmit={handleLogin}>
            <div className="password-gate-input-group">
              <label className="password-gate-input-label" htmlFor="gate-password">
                Enter Site Access Password
              </label>
              <input
                id="gate-password"
                type="password"
                className="password-gate-input"
                value={passwordInput}
                onChange={(e) => setPasswordInput(e.target.value)}
                placeholder="••••••••"
                required
                autoFocus
              />
            </div>

            {errorMsg && <div className="password-gate-error">{errorMsg}</div>}

            <button type="submit" className="password-gate-button">
              Unlock Platform
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
