"use client";

import { motion } from "framer-motion";

export type TimelineStatus = "RUNNING" | "UPCOMING" | "RESULTS OUT" | "TO BE STARTED";

export interface TimelineItem {
  date: string;
  title: string;
  description: string;
  status: TimelineStatus;
}

export const timelineData: TimelineItem[] = [
  {
    date: "7 MAY 2026",
    title: "Registration\nOpens",
    description: "Start your HH Goa\njourney",
    status: "RUNNING",
  },
  {
    date: "AUGUST 2026",
    title: "Open Trials",
    description: "Skill-based\nchallenges open\nto everyone",
    status: "RUNNING",
  },
  {
    date: "EARLY SEPT",
    title: "Alpha Selection",
    description: "First shortlist\nfrom open trials\nperformance",
    status: "RESULTS OUT",
  },
  {
    date: "EARLY SEPT",
    title: "Beta Selection",
    description: "Deeper technical\n& portfolio\nreview",
    status: "RUNNING",
  },
  {
    date: "MID SEPT",
    title: "Onsite Selection",
    description: "Final interviews\n& team-fit\nassessment",
    status: "TO BE STARTED",
  },
];

function StatusBadge({ status }: { status: TimelineStatus }) {
  const styles: Record<TimelineStatus, string> = {
    RUNNING: "bg-[#F6BE2C] text-[#0A261A] font-bold",
    UPCOMING: "border border-[#8E7E5E] text-[#63553A] bg-transparent",
    "RESULTS OUT": "bg-[#073523] text-[#FFF8E8] font-bold",
    "TO BE STARTED": "border border-[#C5B182] text-[#8C7A58] bg-transparent",
  };

  return (
    <span
      className={`label-upper inline-block px-3 py-1 text-[9px] rounded-sm tracking-wider ${styles[status]}`}
    >
      {status}
    </span>
  );
}

export default function Timeline() {
  return (
    <section className="bg-[#F7F0DD] paper-texture py-16 lg:py-24 border-t border-[#E5D7B5]" id="timeline">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        
        {/* Header */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="label-upper mb-2 text-[#FF007A] font-bold tracking-[0.22em]">
            The Timeline
          </p>
          <h2 className="editorial-heading text-4xl sm:text-5xl text-[#073523] font-bold">
            Key Dates
          </h2>
          <div className="mt-3 flex items-center justify-center gap-1.5 text-[#E60067] text-xs font-serif select-none">
            <span>✦</span>
            <span>◆</span>
            <span>✦</span>
          </div>
        </motion.div>

        {/* ── DESKTOP HORIZONTAL TIMELINE CARDS ── */}
        <div className="mt-14 hidden lg:block">
          <div className="grid grid-cols-5 gap-4">
            {timelineData.map((item, i) => (
              <motion.div
                key={`${item.date}-${item.title}`}
                className="flex flex-col items-center text-center"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
              >
                {/* Milestone White Card */}
                <div className="w-full min-h-[175px] rounded-xl border border-[#E5D7B5] bg-[#FFFDF8] p-5 shadow-sm flex flex-col justify-between items-center transition-transform hover:-translate-y-1">
                  <div>
                    <p className="text-[10px] font-bold tracking-widest text-[#8C7A58] uppercase">
                      {item.date}
                    </p>
                    <p className="editorial-heading mt-2.5 whitespace-pre-line text-lg text-[#073523] font-bold leading-tight">
                      {item.title}
                    </p>
                    <p className="mt-2 whitespace-pre-line text-[11px] leading-relaxed text-[#567364] font-medium">
                      {item.description}
                    </p>
                  </div>

                  <div className="mt-4">
                    <StatusBadge status={item.status} />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Connected timeline rail with node dots */}
          <div className="relative mt-8 flex items-center justify-between px-12">
            {/* Axis Line */}
            <div className="absolute left-10 right-10 top-1/2 -translate-y-1/2 h-[2px] border-b-2 border-dotted border-[#D4C39C]" />
            
            {/* Node dots */}
            {[
              { color: "#F6BE2C" },
              { color: "#FF007A" },
              { color: "#073523" },
              { color: "#FF007A" },
              { color: "#F6BE2C" },
            ].map((node, i) => (
              <div
                key={i}
                className="relative z-10 h-3.5 w-3.5 rounded-full border-2 border-[#FFFDF8] shadow-sm"
                style={{ backgroundColor: node.color }}
              />
            ))}
          </div>
        </div>

        {/* ── MOBILE VERTICAL TIMELINE ── */}
        <div className="mt-12 space-y-6 lg:hidden">
          {timelineData.map((item, i) => (
            <motion.div
              key={`${item.date}-${item.title}-mobile`}
              className="relative rounded-xl border border-[#E5D7B5] bg-[#FFFDF8] p-5 shadow-sm"
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.06 }}
            >
              <div className="flex items-center justify-between gap-4">
                <p className="text-[10px] font-bold tracking-widest text-[#8C7A58] uppercase">
                  {item.date}
                </p>
                <StatusBadge status={item.status} />
              </div>
              <p className="editorial-heading mt-2 text-xl text-[#073523] font-bold">
                {item.title.replace("\n", " ")}
              </p>
              <p className="mt-1 text-xs text-[#567364]">
                {item.description.replace(/\n/g, " ")}
              </p>
            </motion.div>
          ))}
        </div>

      </div>
    </section>
  );
}
