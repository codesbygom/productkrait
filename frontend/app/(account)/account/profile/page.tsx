"use client";

import Link from "next/link";
import { useState } from "react";
import { AccountPage } from "@/components/account/AccountShell";
import { errorMessages } from "@/lib/format";
import { api, ApiError, fullName, useSession } from "@/lib/session";
import type { Profile } from "@/lib/types";

type Fields = Pick<Profile, "first_name" | "last_name" | "email"> & { phone: string; city: string; zipcode: string; address: string };

// Same fields and order as account.forms.ProfileForm, rendered like |crispy.
const FIELDS: { name: keyof Fields; label: string; type?: string; help?: string }[] = [
  { name: "first_name", label: "First name" },
  { name: "last_name", label: "Last name" },
  { name: "email", label: "Email address", type: "email" },
  { name: "phone", label: "Phone" },
  { name: "city", label: "City" },
  { name: "zipcode", label: "Zipcode" },
  { name: "address", label: "Address", type: "textarea", help: "Used to pre-fill the shipping address at checkout." },
];

// templates/Account/profile.html
export default function ProfilePage() {
  const { user, reloadUser } = useSession();
  const [form, setForm] = useState<Fields>(() => ({
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    email: user?.email ?? "",
    phone: user?.phone?.toString() ?? "",
    city: user?.city ?? "",
    zipcode: user?.zipcode?.toString() ?? "",
    address: user?.address ?? "",
  }));
  const [message, setMessage] = useState<{ kind: "success" | "danger"; lines: string[] } | null>(null);
  const [busy, setBusy] = useState(false);

  if (!user) return null;

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      // phone and zipcode are IntegerFields: send null rather than "".
      const body = { ...form, phone: form.phone || null, zipcode: form.zipcode || null };
      await api("account/profile/", { method: "PATCH", body: JSON.stringify(body) });
      await reloadUser();
      setMessage({ kind: "success", lines: ["Your profile was saved."] });
    } catch (err) {
      setMessage({ kind: "danger", lines: err instanceof ApiError ? errorMessages(err.data) : ["Could not save your profile."] });
    } finally {
      setBusy(false);
    }
  };

  return (
    <AccountPage title="User Profile">
      Welcome, {fullName(user)}
      <form onSubmit={submit}>
        {message && (
          <div className={`alert alert-${message.kind} mt-2`}>
            {message.lines.map((line) => <div key={line}>{line}</div>)}
          </div>
        )}
        {FIELDS.map((field) => (
          <div className="form-group" key={field.name}>
            <label htmlFor={field.name}>{field.label}</label>
            {field.type === "textarea" ? (
              <textarea
                className="form-control"
                id={field.name}
                rows={2}
                value={form[field.name]}
                onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
              />
            ) : (
              <input
                className="form-control"
                id={field.name}
                type={field.type ?? "text"}
                value={form[field.name]}
                onChange={(e) => setForm({ ...form, [field.name]: e.target.value })}
              />
            )}
            {field.help && <small className="form-text text-muted">{field.help}</small>}
          </div>
        ))}
        <button className="btn btn-success" disabled={busy}>Save</button>{" "}
        <Link className="btn btn-outline-secondary" href="/account/password/">Change password</Link>
      </form>
      <br />
    </AccountPage>
  );
}
