"use client";

import { useState } from "react";

// Pieces of the login100 template markup that login.html, signup.html and
// the password reset pages repeat.

export function AuthHeader({ heading, className = "" }: { heading: string; className?: string }) {
  return (
    <>
      <span className="login100-form-title p-b-26">
        <a href="/">
          <img src="/images/productkrait-navbar-logo.png" alt="ProductKrait" style={{ height: 110, width: "auto" }} />
        </a>
      </span>
      <span className={`login100-form-title p-b-48 ${className}`}>{heading}</span>
    </>
  );
}

export function Errors({ messages }: { messages: string[] }) {
  if (messages.length === 0) return null;
  return (
    <div className="errors">
      {messages.map((m) => (
        <span key={m}>
          {m}
          <br />
        </span>
      ))}
    </div>
  );
}

interface FieldProps {
  name: string;
  label: string;
  type?: string;
  value: string;
  onChange: (value: string) => void;
  autoComplete?: string;
}

// .wrap-input100 with the floating placeholder; main.js adds .has-val
// once the input has text, and the eye button toggles password visibility.
export function Field({ name, label, type = "text", value, onChange, autoComplete }: FieldProps) {
  const [visible, setVisible] = useState(false);
  const isPassword = type === "password";

  return (
    <div className="wrap-input100 validate-input">
      {isPassword && (
        <span className="btn-show-pass" onClick={() => setVisible((v) => !v)}>
          <i className={`fas ${visible ? "fa-eye-slash" : "fa-eye"}`} />
        </span>
      )}
      <input
        className={`input100${value ? " has-val" : ""}`}
        id={name}
        name={name}
        type={isPassword && visible ? "text" : type}
        value={value}
        autoComplete={autoComplete}
        onChange={(e) => onChange(e.target.value)}
        required
      />
      <span className="focus-input100" data-placeholder={label} />
    </div>
  );
}

// The gradient submit button with the cursor-tracking glow.
export function SubmitButton({ children, busy, className = "" }: { children: React.ReactNode; busy?: boolean; className?: string }) {
  return (
    <div className="container-login100-form-btn">
      <div
        className="wrap-login100-form-btn"
        onMouseMove={(e) => {
          const rect = e.currentTarget.getBoundingClientRect();
          e.currentTarget.style.setProperty("--mx", `${e.clientX - rect.left}px`);
          e.currentTarget.style.setProperty("--my", `${e.clientY - rect.top}px`);
        }}
      >
        <div className="login100-form-bgbtn" />
        <button className={`login100-form-btn ${className}`} disabled={busy}>
          {busy ? <i className="fas fa-spinner fa-spin" /> : children}
        </button>
      </div>
    </div>
  );
}
