"use client";

import { useState } from "react";
import { AuthHeader, Errors, Field, SubmitButton } from "@/components/auth/AuthForm";
import { errorMessages } from "@/lib/format";
import { api, ApiError } from "@/lib/session";

// templates/Account/password_reset_form.html + password_reset_done.html
export default function PasswordResetPage() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErrors([]);
    try {
      await api("account/forget-password/", {
        method: "POST",
        body: JSON.stringify({ email, redirect_url: `${window.location.origin}/account/password-reset/` }),
      });
      setSent(true);
    } catch (err) {
      setErrors(err instanceof ApiError ? errorMessages(err.data) : ["Could not reach the server."]);
    } finally {
      setBusy(false);
    }
  };

  if (sent) {
    return (
      <div className="login100-form">
        <AuthHeader heading="Check your email" />
        <p className="txt1">If that email is registered, we have sent you a link to choose a new password.</p>
        <div className="text-center p-t-40">
          <a className="txt2" href="/account/login/">Back to log in</a>
        </div>
      </div>
    );
  }

  return (
    <form className="login100-form" onSubmit={submit}>
      <AuthHeader heading="Reset password" />
      <p className="txt1 p-b-20">Enter the email you signed up with and we&apos;ll send you a link to choose a new password.</p>
      <Errors messages={errors} />
      <Field name="email" label="Email" type="email" value={email} onChange={setEmail} autoComplete="email" />
      <SubmitButton busy={busy}>Send reset link</SubmitButton>
      <div className="text-center p-t-40">
        <a className="txt2" href="/account/login/">Back to log in</a>
      </div>
    </form>
  );
}
