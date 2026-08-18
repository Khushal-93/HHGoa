"use client";

import Link from "next/link";
import { useState } from "react";
import { Upload } from "lucide-react";

export default function SubmitPage() {
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
            <li>
              <Link href="/tasks/voice-enabled-rag" className="hover:text-[var(--pink)]">
                TASK
              </Link>
            </li>
            <li aria-hidden="true">&gt;</li>
            <li className="text-[var(--pink)]">SUBMIT</li>
          </ol>
        </nav>

        <p className="label-upper mb-3 text-[var(--pink)]">Submission</p>
        <h1 className="editorial-heading text-[clamp(2rem,4vw,3rem)] text-[var(--text-on-light)]">
          Submit Your Project
        </h1>
        <p className="mt-4 text-sm text-[var(--text-on-light-muted)]">
          Voice-Enabled RAG Model — Deadline: 13 Aug 2026, 11:59 PM IST
        </p>

        {submitted ? (
          <div className="mt-10 border border-[var(--tropical)] bg-[var(--cream)] p-8 text-center">
            <p className="editorial-heading text-2xl text-[var(--text-on-light)]">
              Submission received!
            </p>
            <p className="mt-3 text-sm text-[var(--text-on-light-muted)]">
              Good luck. Results will be announced during the selection phase.
            </p>
            <Link href="/tasks/voice-enabled-rag" className="btn-primary mt-6 inline-flex">
              Back to Task
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-10 space-y-5">
            <div>
              <label htmlFor="repo" className="label-upper mb-2 block text-[var(--text-on-light-muted)]">
                Repository URL
              </label>
              <input
                id="repo"
                name="repo"
                type="url"
                required
                placeholder="https://github.com/..."
                className="w-full border border-[var(--beige)] bg-[var(--cream)] px-4 py-3 text-sm text-[var(--text-on-light)] focus:border-[var(--pink)] focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="demo" className="label-upper mb-2 block text-[var(--text-on-light-muted)]">
                Demo Video URL
              </label>
              <input
                id="demo"
                name="demo"
                type="url"
                required
                placeholder="https://..."
                className="w-full border border-[var(--beige)] bg-[var(--cream)] px-4 py-3 text-sm text-[var(--text-on-light)] focus:border-[var(--pink)] focus:outline-none"
              />
            </div>
            <div>
              <label htmlFor="notes" className="label-upper mb-2 block text-[var(--text-on-light-muted)]">
                Notes (optional)
              </label>
              <textarea
                id="notes"
                name="notes"
                rows={4}
                className="w-full border border-[var(--beige)] bg-[var(--cream)] px-4 py-3 text-sm text-[var(--text-on-light)] focus:border-[var(--pink)] focus:outline-none"
              />
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 bg-[var(--pink)] px-6 py-3 text-xs font-bold uppercase tracking-wider text-white transition-transform hover:-translate-y-0.5"
            >
              <Upload size={16} />
              Submit Project
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
