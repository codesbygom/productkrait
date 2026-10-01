"use client";

import { useState } from "react";
import { AuthHeader, Errors, Field, SubmitButton } from "@/components/auth/AuthForm";
import { errorMessages } from "@/lib/format";
import { api, ApiError, useSession } from "@/lib/session";

const EMPTY = { username: "", first_name: "", last_name: "", email: "", password1: "", password2: "" };

// templates/Account/signup.html
export default function SignupPage() {
  const { login } = useSession();
  const [form, setForm] = useState(EMPTY);
  const [errors, setErrors] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const set = (field: keyof typeof EMPTY) => (value: string) => setForm((f) => ({ ...f, [field]: value }));

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.password1 !== form.password2) {
      setErrors(["The two password fields didn't match."]);
      return;
    }
    setBusy(true);
    setErrors([]);
    try {
      const { password1, password2: _, ...profile } = form;
      await api("account/register/", {
        method: "POST",
        body: JSON.stringify({ ...profile, password: password1, redirect_url: `${window.location.origin}/account/profile/` }),
      });
      // The Django signup view logs the new user straight in; do the same.
      await login(form.email, password1);
      window.location.href = "/";
    } catch (err) {
      setErrors(err instanceof ApiError ? errorMessages(err.data) : ["Could not reach the server."]);
      setBusy(false);
    }
  };

  return (
    <form className="login100-form validate-form" onSubmit={submit}>
      <AuthHeader heading="Create Account" className="myfont" />
      <Errors messages={errors} />
      <Field name="username" label="Username" value={form.username} onChange={set("username")} autoComplete="username" />
      <Field name="first_name" label="First name" value={form.first_name} onChange={set("first_name")} autoComplete="given-name" />
      <Field name="last_name" label="Last name" value={form.last_name} onChange={set("last_name")} autoComplete="family-name" />
      <Field name="email" label="Email" type="email" value={form.email} onChange={set("email")} autoComplete="email" />
      <Field name="password1" label="Password" type="password" value={form.password1} onChange={set("password1")} autoComplete="new-password" />
      <Field name="password2" label="Confirm password" type="password" value={form.password2} onChange={set("password2")} autoComplete="new-password" />
      <SubmitButton busy={busy} className="myfont">Sign Up</SubmitButton>

      <div className="text-center p-t-115">
        <span className="myfont txt1">Already have an account? </span>
        <a className="txt2 myfont" href="/account/login/">Log In</a>
      </div>
    </form>
  );
}
