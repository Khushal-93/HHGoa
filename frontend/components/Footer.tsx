import Link from "next/link";
import TropicalPattern from "./TropicalPattern";

const footerLinks = [
  { href: "/", label: "Home" },
  { href: "/timeline", label: "Timeline" },
  { href: "/tasks", label: "Tasks" },
  { href: "/notice-board", label: "Notice Board" },
  { href: "/faq", label: "FAQ" },
];

const socialLinks = [
  { href: "https://github.com", label: "GitHub" },
  { href: "https://x.com", label: "X / Twitter" },
  { href: "https://discord.com", label: "Discord" },
  { href: "https://linkedin.com", label: "LinkedIn" },
];

function FooterIllustration() {
  return (
    <svg viewBox="0 0 120 60" className="h-10 w-24 opacity-70" aria-hidden="true">
      {/* Palm silhouettes */}
      <line x1="20" y1="55" x2="22" y2="20" stroke="#18744a" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M22 20 Q8 12 2 18 Q12 20 22 20" fill="#18744a" />
      <path d="M22 20 Q36 10 42 16 Q34 20 22 20" fill="#18744a" />
      <path d="M22 20 Q22 8 25 2 Q24 12 22 20" fill="#2a8f5e" />
      {/* Sun rising */}
      <circle cx="60" cy="50" r="18" fill="#F5C51B" opacity="0.85" />
      <circle cx="60" cy="50" r="22" fill="#F5C51B" opacity="0.2" />
      {/* Right palm */}
      <line x1="100" y1="55" x2="98" y2="22" stroke="#18744a" strokeWidth="2.5" strokeLinecap="round" />
      <path d="M98 22 Q84 14 78 20 Q88 22 98 22" fill="#18744a" />
      <path d="M98 22 Q112 12 118 18 Q110 22 98 22" fill="#18744a" />
      <path d="M98 22 Q97 8 95 2 Q96 12 98 22" fill="#2a8f5e" />
      {/* Ocean shimmer */}
      <path d="M0 55 Q30 52 60 55 Q90 58 120 55" fill="none" stroke="#18744a" strokeWidth="1" opacity="0.5" />
    </svg>
  );
}

export default function Footer() {
  return (
    <footer className="relative border-t border-[var(--border-muted)] bg-[var(--forest-black)]">
      <TropicalPattern className="h-3" />
      <div className="mx-auto max-w-7xl px-5 py-14 lg:px-8">
        <div className="grid gap-10 md:grid-cols-3">
          {/* Brand */}
          <div>
            <p className="editorial-heading text-4xl text-[var(--gold)]">
              HACKER
            </p>
            <p className="editorial-heading text-4xl text-[var(--cream)]">
              HOUSE
            </p>
            <p className="mt-1 text-sm font-medium tracking-widest text-[var(--gold)]/60">
              GOA 2026
            </p>
            <p className="mt-5 max-w-xs text-sm leading-relaxed text-[var(--text-on-dark-muted)]">
              28–31 Oct 2026 • Build voice-enabled RAG systems with the best
              builders in Goa.
            </p>
            <div className="mt-5">
              <FooterIllustration />
            </div>
          </div>

          {/* Links */}
          <div>
            <p className="label-upper mb-5 text-[var(--gold)]">Navigate</p>
            <ul className="space-y-3">
              {footerLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="group flex items-center gap-2 text-sm text-[var(--text-on-dark-muted)] transition-colors hover:text-[var(--cream)]"
                  >
                    <span className="h-px w-3 bg-[var(--border-gold)] transition-all group-hover:w-5 group-hover:bg-[var(--gold)]" />
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Social */}
          <div>
            <p className="label-upper mb-5 text-[var(--gold)]">Community</p>
            <ul className="space-y-3">
              {socialLinks.map((link) => (
                <li key={link.label}>
                  <a
                    href={link.href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="group flex items-center gap-2 text-sm text-[var(--text-on-dark-muted)] transition-colors hover:text-[var(--cream)]"
                  >
                    <span className="h-px w-3 bg-[var(--border-gold)] transition-all group-hover:w-5 group-hover:bg-[var(--gold)]" />
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-[var(--border-muted)] pt-8 sm:flex-row">
          <p className="text-xs text-[var(--text-on-dark-muted)]">
            © 2026 Hacker House Goa. All rights reserved.
          </p>
          <p className="text-xs text-[var(--text-on-dark-muted)]">
            28–31 Oct 2026 • Goa, India
          </p>
        </div>
      </div>
    </footer>
  );
}
