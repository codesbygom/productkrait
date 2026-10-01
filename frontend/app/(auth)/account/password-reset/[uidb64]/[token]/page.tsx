"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { AuthHeader, Errors, Field, SubmitButton } from "@/components/auth/AuthForm";
import { errorMessages } from "@/lib/format";
import { api, ApiError } from "@/lib/session";

// templates/Account/password_reset_confirm.html + password_reset_complete.html
export default function PasswordResetConfirmPage() {
  const { uidb64, token } = useParams<{ uidb64: string; token: string }>();
  const [password, setPassword] = useState("");
  const [confirmed, setConfirmed] = useState("");
  const [done, setDone] = useState(false);
  const [errors, setErrors] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErrors([]);
    try {
      await api(`account/reset-password/${uidb64}/${token}/`, {
        method: "PUT",
        body: JSON.stringify({ new_password: password, confirmed_password: confirmed }),
      });
      setDone(true);
    } catch (err) {
      setErrors(err instanceof ApiError ? errorMessages(err.data) : ["Could not reach the server."]);
    } finally {
      setBusy(false);
    }
  };

  if (done) {
    return (
      <div className="login100-form">
        <AuthHeader heading="Password changed" />
        <p className="txt1">Your password has been set. You can log in with it now.</p>
        <div className="text-center p-t-40">
          <a className="txt2" href="/account/login/">Log in</a>
        </div>
      </div>
    );
  }

  return (
    <form className="login100-form" onSubmit={submit}>
      <AuthHeader heading="New password" />
      <Errors messages={errors} />
      <Field name="new_password" label="New password" type="password" value={password} onChange={setPassword} autoComplete="new-password" />
      <Field name="confirmed_password" label="Confirm new password" type="password" value={confirmed} onChange={setConfirmed} autoComplete="new-password" />
      <SubmitButton busy={busy}>Save password</SubmitButton>
      <div className="text-center p-t-40">
        <a className="txt2" href="/account/password-reset/">Request a new link</a>
      </div>
    </form>
  );
}
