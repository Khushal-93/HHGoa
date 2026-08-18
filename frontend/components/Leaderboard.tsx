"use client";

import Link from "next/link";
import { motion } from "framer-motion";

const rows = [
  { rank: "#1", team: "Nexus", latency: "118ms", accuracy: "93.4%", status: "ON TRACK" },
  { rank: "#2", team: "Binary Brains", latency: "142ms", accuracy: "90.1%", status: "ON TRACK" },
  { rank: "#3", team: "404 Found", latency: "165ms", accuracy: "88.7%", status: "ON TRACK" },
  { rank: "#4", team: "Packet Loss", latency: "189ms", accuracy: "86.3%", status: "ON TRACK" },
  { rank: "#5", team: "Ctrl Alt Elite", latency: "198ms", accuracy: "85.9%", status: "ON TRACK" },
];

export default function Leaderboard() {
  return (
    <section className="bg-[#05281A] py-16 lg:py-24 border-t border-[#144833]/60" id="leaderboard">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        
        {/* Header with View All Button */}
        <div className="mb-8 flex items-center justify-between">
          <motion.h2
            className="editorial-heading text-3xl sm:text-4xl lg:text-5xl uppercase text-[#FFF8E8] font-bold tracking-tight"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            Live Leaderboard
          </motion.h2>

          <Link
            href="#"
            className="rounded-md border border-[#1E5D3F] px-4 py-1.5 text-xs font-semibold text-[#EDE3C9] transition-colors hover:border-[#F6BE2C] hover:text-[#F6BE2C]"
          >
            View All
          </Link>
        </div>

        {/* Table Container */}
        <motion.div
          className="overflow-hidden rounded-xl border border-[#185338] bg-[#073523]/80 shadow-lg shadow-black/20"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <div className="overflow-x-auto">
            <table className="w-full min-w-[620px] text-left text-sm">
              <thead>
                <tr className="border-b border-[#144833] bg-[#042015]/90">
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-[#A59475]">
                    RANK
                  </th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-[#A59475]">
                    TEAM
                  </th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-[#A59475]">
                    LATENCY (P50)
                  </th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-[#A59475]">
                    ACCURACY
                  </th>
                  <th className="px-6 py-4 text-[10px] font-bold uppercase tracking-wider text-[#A59475]">
                    STATUS
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#144833]/60">
                {rows.map((row) => (
                  <tr
                    key={row.team}
                    className="transition-colors hover:bg-[#093D2A]"
                  >
                    <td className="px-6 py-4 font-mono text-sm font-semibold text-[#FFF8E8]">
                      {row.rank}
                    </td>
                    <td className="px-6 py-4 font-medium text-[#FFF8E8]">
                      {row.team}
                    </td>
                    <td className="px-6 py-4 text-[#EDE3C9]">
                      {row.latency}
                    </td>
                    <td className="px-6 py-4 text-[#EDE3C9]">
                      {row.accuracy}
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-block rounded border border-[#1C7D47] px-2.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[#38B36E] bg-[#1C7D47]/10">
                        {row.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>

      </div>
    </section>
  );
}
