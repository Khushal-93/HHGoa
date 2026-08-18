import Link from "next/link";
import Timeline from "@/components/Timeline";

export default function TimelinePage() {
  return (
    <div className="forest-texture min-h-screen">
      <div className="mx-auto max-w-7xl px-5 py-12 lg:px-8 lg:py-16">
        <nav aria-label="Breadcrumb" className="mb-8">
          <ol className="flex flex-wrap gap-2 text-xs tracking-wider text-[var(--text-on-dark-muted)]">
            <li>
              <Link href="/" className="hover:text-[var(--gold)]">
                HOME
              </Link>
            </li>
            <li aria-hidden="true">&gt;</li>
            <li className="text-[var(--gold)]">TIMELINE</li>
          </ol>
        </nav>
      </div>
      <Timeline />
    </div>
  );
}
