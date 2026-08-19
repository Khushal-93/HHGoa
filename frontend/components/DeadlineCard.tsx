"use client";

import Link from "next/link";

export default function DeadlineCard() {
  return (
    <div className="flex flex-col gap-4 rounded-xl border border-[#E5D7B5] bg-[#FFFDF8] p-6 sm:flex-row sm:items-center sm:justify-between shadow-sm">
      <div>
        <p className="label-upper text-[#FF007A] font-bold tracking-widest text-[11px]">
          Deadline
        </p>
        <p className="mt-1 text-base sm:text-lg font-bold text-[#073523]">
          13 AUG 2026, 11:59 PM IST
        </p>
      </div>

      <Link
        href="/submit"
        className="inline-flex items-center justify-center gap-2 rounded-lg bg-[#E60067] px-6 py-3 text-xs font-bold uppercase tracking-wider text-white transition-transform hover:scale-[1.02] active:scale-[0.98] shadow-md shadow-[#E60067]/20"
      >
        <span>Submit Your Project</span>
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M2 12L12 2M12 2H4M12 2V10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </Link>
    </div>
  );
}
