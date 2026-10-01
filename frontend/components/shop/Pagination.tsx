import Link from "next/link";

const PAGE_SIZE = 12; // REST_FRAMEWORK["PAGE_SIZE"]

interface Props {
  count: number;
  page: number;
  href: (page: number) => string;
}

export function pageNumber(value: string | undefined): number {
  const page = Number(value);
  return Number.isInteger(page) && page > 0 ? page : 1;
}

// The Bootstrap pagination block the Django list templates render.
export default function Pagination({ count, page, href }: Props) {
  const pages = Math.ceil(count / PAGE_SIZE);
  if (pages <= 1) return null;

  return (
    <nav aria-label="Page navigation" className="mt-4">
      <ul className="pagination justify-content-center">
        <li className={`page-item${page > 1 ? "" : " disabled"}`}>
          <Link className="page-link" href={page > 1 ? href(page - 1) : "#"} aria-label="Previous">
            <span aria-hidden="true">&laquo;</span>
          </Link>
        </li>
        {Array.from({ length: pages }, (_, i) => i + 1).map((n) => (
          <li key={n} className={`page-item${n === page ? " active" : ""}`}>
            {n === page ? <span className="page-link">{n}</span> : <Link className="page-link" href={href(n)}>{n}</Link>}
          </li>
        ))}
        <li className={`page-item${page < pages ? "" : " disabled"}`}>
          <Link className="page-link" href={page < pages ? href(page + 1) : "#"} aria-label="Next">
            <span aria-hidden="true">&raquo;</span>
          </Link>
        </li>
      </ul>
    </nav>
  );
}
