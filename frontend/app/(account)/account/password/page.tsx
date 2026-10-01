"use client";

import { useState } from "react";
import { AccountPage } from "@/components/account/AccountShell";
import { errorMessages } from "@/lib/format";
import { api, ApiError } from "@/lib/session";

const EMPTY = { old_password: "", new_password: "", confirmed_password: "" };

const FIELDS: { name: keyof typeof EMPTY; label: string; autoComplete: string }[] = [
  { name: "old_password", label: "Old password", autoComplete: "current-password" },
  { name: "new_password", label: "New password", autoComplete: "new-password" },
  { name: "confirmed_password", label: "New password confirmation", autoComplete: "new-password" },
];

// templates/Account/password_change.html
export default function PasswordChangePage() {
  const [form, setForm] = useState(EMPTY);
  const [message, setMessage] = useState<{ kind: "success" | "danger"; lines: string[] } | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api("account/change-password/", { method: "PUT", body: JSON.stringify(form) });
      setForm(EMPTY);
      setMessage({ kind: "success", lines: ["Your password was changed."] });
    } catch (err) {
      setMessage({ kind: "danger", lines: err instanceof ApiError ? errorMessages(err.data) : ["Could not change your password."] });
    } finally {
      setBusy(false);
    }
  };

  return (
    <AccountPage title="Change password">
      <form onSubmit={submit}>
        {message && (
          <div className={`alert alert-${message.kind}`}>
            {message.lines.map((line) => <div key={line}>{line}</div>)}
          </div>
        )}
        {FIELDS.map((field) => (
          <div className="form-group" key={field.name}>
            <label htmlFor={field.name}>{field.label}</label>
            <input
              className="form-control"
              id={field.name}
              type="password"
              autoComplete={field.autoComplete}
              value={form[field.name]}
              onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
              required
            />
          </div>
        ))}
        <button className="btn btn-success" disabled={busy}>Change password</button>
      </form>
    </AccountPage>
  );
}
