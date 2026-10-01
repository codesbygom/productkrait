import Link from "next/link";

export default function NotFound() {
  return (
    <div className="text-center py-5">
      <h1 className="display-4">404</h1>
      <p className="lead">The page you are looking for could not be found.</p>
      <Link href="/" className="btn btn-primary">
        <i className="fas fa-arrow-left" /> Back to ProductKrait
      </Link>
    </div>
  );
}
