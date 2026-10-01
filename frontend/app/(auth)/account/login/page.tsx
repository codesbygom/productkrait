"use client";

import { useState } from "react";
import { AuthHeader, Errors, Field, SubmitButton } from "@/components/auth/AuthForm";
import { errorMessages } from "@/lib/format";
import { ApiError, useSession } from "@/lib/session";

// Only same-site paths, so ?next= can't bounce users to another site.
function nextPath(): string {
  const next = new URLSearchParams(window.location.search).get("next") ?? "";
  return next.startsWith("/") && !next.startsWith("//") ? next : "/";
}

// templates/Account/login.html
export default function LoginPage() {
  const { login } = useSession();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setErrors([]);
    try {
      await login(email, password);
      window.location.href = nextPath();
    } catch (err) {
      setErrors(err instanceof ApiError ? errorMessages(err.data) : ["Could not reach the server."]);
      setBusy(false);
    }
  };

  return (
    <form className="login100-form validate-form" onSubmit={submit}>
      <AuthHeader heading="Log In" />
      <Errors messages={errors} />
      <Field name="email" label="Email" type="email" value={email} onChange={setEmail} autoComplete="email" />
      <Field name="password" label="Password" type="password" value={password} onChange={setPassword} autoComplete="current-password" />
      <SubmitButton busy={busy}>Log In</SubmitButton>

      <div className="text-center p-t-20">
        <a className="txt2" href="/account/password-reset/">Forgot your password?</a>
      </div>
      <div className="text-center p-t-80">
        <span className="txt1">Don&apos;t have an account? </span>
        <a className="txt2" href="/account/signup/">Sign up</a>
      </div>
    </form>
  );
}
