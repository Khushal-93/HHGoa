"use client";

import Link from "next/link";
import { useState } from "react";

export default function RegisterPage() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitted(true);
  }

  return (
    <div className="paper-texture min-h-screen py-12 lg:py-16">
      <div className="mx-auto max-w-lg px-5 lg:px-8">
        <nav aria-label="Breadcrumb" className="mb-8">
          <ol className="flex flex-wrap gap-2 text-xs tracking-wider text-[var(--text-on-light-muted)]">
            <li>
              <Link href="/" className="hover:text-[var(--pink)]">
                HOME
              </Link>
            </li>
            <li aria-hidden="true">&gt;</li>
            <li className="text-[var(--pink)]">REGISTER</li>
          </ol>
        </nav>

        <p className="label-upper mb-3 text-[var(--pink)]">Join Us</p>
        <h1 className="editorial-heading text-[clamp(2rem,4vw,3rem)] text-[var(--text-on-light)]">
          Register for HH Goa 2026
        </h1>
        <p className="mt-4 text-sm text-[var(--text-on-light-muted)]">
          28–31 Oct 2026 • Goa, India. Start your journey with open trials.
        </p>

        {submitted ? (
          <div className="mt-10 border border-[var(--tropical)] bg-[var(--cream)] p-8 text-center">
            <p className="editorial-heading text-2xl text-[var(--text-on-light)]">
              You&apos;re on the list!
            </p>
            <p className="mt-3 text-sm text-[var(--text-on-light-muted)]">
              We&apos;ll send you updates about trials and selection phases.
            </p>
            <Link href="/" className="btn-primary mt-6 inline-flex">
              Back to Home
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-10 space-y-5">
            <div>
              <label htmlFor="name" className="label-upper mb-2 block text-[var(--text-on-light-muted)]">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                required
                className="w-full border border-[var(--beige)] bg-[var(--cream)] px-4 py-3 text-sm text-[var(--text-on-light)] focus:border-[var(--pink)] focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="email" className="label-upper mb-2 block text-[var(--text-on-light-muted)]">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="w-full border border-[var(--beige)] bg-[var(--cream)] px-4 py-3 text-sm text-[var(--text-on-light)] focus:border-[var(--pink)] focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="team" className="label-upper mb-2 block text-[var(--text-on-light-muted)]">
                Team Name (optional)
              </label>
              <input
                id="team"
                name="team"
                className="w-full border border-[var(--beige)] bg-[var(--cream)] px-4 py-3 text-sm text-[var(--text-on-light)] focus:border-[var(--pink)] focus:outline-none"
              />
            </div>
            <button type="submit" className="btn-primary w-full">
              Register Now
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
