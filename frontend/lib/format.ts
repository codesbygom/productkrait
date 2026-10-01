export const NO_IMAGE = "/images/no-image.svg";

// DRF builds absolute image URLs from whatever host it was reached on
// (127.0.0.1:8000 for server-side fetches). Keep only the path so images
// always load through the /media proxy.
export function mediaUrl(url: string | null | undefined): string {
  if (!url) return NO_IMAGE;
  try {
    return new URL(url, "http://x").pathname;
  } catch {
    return url;
  }
}

export function toman(value: string | number, digits = 0): string {
  return `${Number(value).toLocaleString("en-US", { maximumFractionDigits: digits })} Toman`;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}/${pad(d.getMonth() + 1)}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

export function truncate(html: string, length: number): string {
  const text = html.replace(/<[^>]*>/g, "").replace(/\s+/g, " ").trim();
  return text.length > length ? `${text.slice(0, length - 1)}…` : text;
}

// Flattens DRF validation errors ({field: [msg]} / {detail: msg}) into lines.
export function errorMessages(data: unknown): string[] {
  if (!data) return ["Something went wrong."];
  if (typeof data === "string") return [data];
  if (Array.isArray(data)) return data.flatMap(errorMessages);
  if (typeof data === "object") {
    return Object.entries(data as Record<string, unknown>).flatMap(([key, value]) => {
      const messages = errorMessages(value);
      const plain = ["detail", "non_field_errors", "message", "failed"].includes(key);
      return plain ? messages : messages.map((m) => `${key.replace(/_/g, " ")}: ${m}`);
    });
  }
  return [String(data)];
}
