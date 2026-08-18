"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";

export function StudioLogo() {
  return (
    <div className="flex items-center select-none">
      <svg
        viewBox="0 0 130 52"
        className="h-11 w-auto"
        fill="#F6BE2C"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* ── TOP LINE: 2:47PM ── */}
        {/* '2' */}
        <path d="M4 4 H22 V14 H12 V18 H22 V26 H4 V16 H14 V10 H4 Z" />

        {/* ':' Colon */}
        <rect x="25" y="8" width="4.5" height="4.5" rx="1" />
        <rect x="25" y="17" width="4.5" height="4.5" rx="1" />

        {/* '4' */}
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M33 4 H39 V13 H45 V4 H51 V26 H45 V19 H33 Z M39 13 V9 H45 V13 Z"
        />

        {/* '7' */}
        <path d="M54 4 H71 V10 L63 26 H56 L64 10 H54 Z" />

        {/* 'P' */}
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M74 4 H86 C91 4 92 8 92 12 C92 16 91 19 86 19 H80 V26 H74 Z M80 9 H85 C86.5 9 86.5 14 85 14 H80 Z"
        />

        {/* 'M' */}
        <path d="M95 4 H101 L106.5 15 L112 4 H118 V26 H112 V14 L106.5 24 L101 14 V26 H95 Z" />

        {/* ── BOTTOM LINE: STUDIO ── */}
        {/* 'S' */}
        <path d="M12 30 H26 V35 H18 V37 H26 V48 H12 V43 H20 V41 H12 Z" />

        {/* 'T' */}
        <path d="M29 30 H43 V35 H39 V48 H33 V35 H29 Z" />

        {/* 'U' */}
        <path d="M46 30 H52 V42 H56 V30 H62 V48 H46 Z" />

        {/* 'D' */}
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M65 30 H75 C80 30 82 34 82 39 C82 44 80 48 75 48 H65 Z M71 35 H74 C76 35 76 43 74 43 H71 Z"
        />

        {/* 'I' */}
        <path d="M85 30 H91 V48 H85 Z" />

        {/* 'O' */}
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M94 30 H108 C113 30 113 48 108 48 H94 C89 48 89 30 94 30 Z M96 35 H106 C107.5 35 107.5 43 106 43 H96 C94.5 43 94.5 35 96 35 Z"
        />
      </svg>
    </div>
  );
}

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) =>
    href === "/" ? pathname === "/" : pathname.startsWith(href);

  return (
    <header className="sticky top-0 z-50 bg-[#073523]/95 backdrop-blur-md border-b border-[#144833]/60">
      <nav
        className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3 lg:px-10"
        aria-label="Main navigation"
      >
        {/* Exact 2:47PM STUDIO Logo */}
        <Link href="/" className="flex items-center gap-3 group transition-transform hover:scale-105">
          <StudioLogo />
        </Link>

        {/* Navigation Links */}
        <ul className="hidden items-center gap-8 md:flex">
          {[
            { href: "/", label: "Home" },
            { href: "/timeline", label: "Timeline" },
            { href: "/tasks", label: "Tasks" },
            { href: "/notice-board", label: "Notice Board" },
            { href: "/faq", label: "FAQ" },
          ].map((link) => (
            <li key={link.href}>
              <Link
                href={link.href}
                className={`text-[13px] font-bold tracking-wider uppercase transition-colors duration-150 ${
                  isActive(link.href)
                    ? "text-[#F6BE2C]"
                    : "text-[#EDE3C9] hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Right Section: CHECK HYPE Link */}
        <div className="flex items-center gap-6">
          <Link
            href="/tasks"
            className="hidden sm:inline-block text-xs font-bold tracking-widest text-[#FFF8E8] uppercase hover:text-[#F6BE2C] transition-colors"
          >
            CHECK HYPE
          </Link>

          {/* Mobile hamburger */}
          <button
            type="button"
            className="p-1.5 text-[#FFF8E8] md:hidden focus:outline-none"
            onClick={() => setOpen(!open)}
            aria-label={open ? "Close menu" : "Open menu"}
          >
            {open ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Mobile drawer */}
      {open && (
        <div className="border-t border-[#144833] bg-[#041E15] px-6 py-5 md:hidden">
          <ul className="flex flex-col gap-4">
            {[
              { href: "/", label: "Home" },
              { href: "/timeline", label: "Timeline" },
              { href: "/tasks", label: "Tasks" },
              { href: "/notice-board", label: "Notice Board" },
              { href: "/faq", label: "FAQ" },
            ].map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className={`block text-sm font-bold uppercase tracking-wider ${
                    isActive(link.href) ? "text-[#F6BE2C]" : "text-[#EDE3C9]"
                  }`}
                  onClick={() => setOpen(false)}
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </header>
  );
}
