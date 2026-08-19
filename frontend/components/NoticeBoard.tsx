"use client";

import { motion } from "framer-motion";

const notes = [
  {
    label: "Task Update",
    labelColor: "text-[#E60067]",
    content: "Voice model baseline\nadded to starter kit.\nCheck downloads.",
    timestamp: "6 AUG, 10:30 AM",
    rotation: "-1.5deg",
    pinColor: "#E60067",
  },
  {
    label: "Reminder",
    labelColor: "text-[#073523]",
    content: "Submissions closing\non 13 Aug, 11:59 PM IST.\nDon't miss it!",
    timestamp: "3 AUG, 04:15 PM",
    rotation: "1.2deg",
    pinColor: "#F6BE2C",
  },
  {
    label: "Tip",
    labelColor: "text-[#E60067]",
    content: "Measure latency\nproperly. P50, P70,\nP100 matter!",
    timestamp: "3 AUG, 11:20 AM",
    rotation: "-0.8deg",
    pinColor: "#1C7D47",
  },
];

export default function NoticeBoard() {
  return (
    <section className="bg-[#05281A] py-16 lg:py-24 border-t border-[#144833]/60" id="notice-board">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        
        {/* Header */}
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <h2 className="editorial-heading text-4xl sm:text-5xl text-[#FFF8E8] font-bold tracking-tight uppercase">
            Notice Board
          </h2>
        </motion.div>

        {/* Sticky Notes Grid */}
        <div className="mt-14 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {notes.map((note, i) => (
            <motion.article
              key={note.label}
              className="relative rounded-sm bg-[#FFF8E4] p-7 shadow-xl shadow-black/30 border border-[#EADBBD] flex flex-col justify-between min-h-[220px]"
              style={{ transform: `rotate(${note.rotation})` }}
              initial={{ opacity: 0, y: 26 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ scale: 1.03, rotate: "0deg", transition: { duration: 0.2 } }}
            >
              {/* Pushpin at Top */}
              <div
                className="absolute -top-3 left-1/2 -translate-x-1/2 h-6 w-6 rounded-full shadow-md border-2 border-white/60 flex items-center justify-center"
                style={{ backgroundColor: note.pinColor }}
                aria-hidden="true"
              >
                <div className="h-2 w-2 rounded-full bg-white/40" />
              </div>

              <div>
                <p className={`label-upper mb-3 font-extrabold tracking-wider ${note.labelColor}`}>
                  {note.label}
                </p>
                <p className="whitespace-pre-line font-serif text-[17px] leading-relaxed text-[#14261D] font-semibold">
                  {note.content}
                </p>
              </div>

              {/* Timestamp at bottom */}
              <p className="mt-6 text-[11px] font-sans font-medium text-[#8F7D5E] tracking-wide">
                {note.timestamp}
              </p>
            </motion.article>
          ))}
        </div>

      </div>
    </section>
  );
}
