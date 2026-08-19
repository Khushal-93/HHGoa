import { Check } from "lucide-react";

const items = [
  "Working demo with voice input & answer output",
  "Code repository (public)",
  "Latency benchmarks (P50 / P70 / P100)",
  "Short demo video (2-3 min)",
  "README with setup & run instructions",
];

export default function SubmissionChecklist() {
  return (
    <div className="rounded-xl border border-[#E5D7B5] bg-[#FFFDF8] p-6 lg:p-8 shadow-sm">
      <h3 className="label-upper text-xs font-bold tracking-wider text-[#073523] uppercase">
        Submission Checklist
      </h3>
      <ul className="mt-5 space-y-3.5">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-3.5">
            <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#1C7D47]/15 border border-[#1C7D47]/30">
              <Check size={12} className="text-[#1C7D47] stroke-[2.5]" />
            </span>
            <span className="text-sm font-medium text-[#2A5240]">
              {item}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
