"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import type { CategoryNode } from "@/lib/types";

// templates/shop/recursive_category_menu.html: children open on hover.
export default function CategoryMenu({ category, onNavigate }: { category: CategoryNode; onNavigate: () => void }) {
  const params = useParams<{ slug?: string }>();
  const [open, setOpen] = useState(false);
  const active = params.slug === category.slug ? " active" : "";

  const link = (
    <Link className={`dropdown-item text-center px-2 py-2${active}`} href={`/category/${category.slug}/`} onClick={onNavigate}>
      {category.title}
    </Link>
  );

  if (category.children.length === 0) return link;

  return (
    <div className="dropdown-submenu" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      {link}
      <div className="dropdown-menu" style={{ display: open ? "block" : "none" }}>
        {category.children.map((child) => (
          <CategoryMenu key={child.id} category={child} onNavigate={onNavigate} />
        ))}
      </div>
    </div>
  );
}
