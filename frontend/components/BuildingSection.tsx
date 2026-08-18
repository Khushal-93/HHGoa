"use client";

import { motion } from "framer-motion";
import { IconWaveform, IconRAG, IconShield } from "./LineIcons";
import TropicalPattern from "./TropicalPattern";

const cards = [
  {
    icon: IconWaveform,
    title: "1. Transcription",
    description: "Real-time speech\nto text conversion",
  },
  {
    icon: IconRAG,
    title: "2. RAG Pipeline",
    description: "Chunking, retrieval\n& generation",
  },
  {
    icon: IconShield,
    title: "3. Guardrails",
    description: "Safe, grounded,\nand reliable answers",
  },
];

export default function BuildingSection() {
  return (
    <section className="bg-[#05281A] pt-16 pb-0 border-t border-[#144833]/60 relative overflow-hidden">
      <div className="mx-auto max-w-7xl px-6 pb-16 lg:px-10">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <p className="label-upper mb-3 text-[#F6BE2C] tracking-[0.2em] font-bold">
            At a Glance
          </p>
          <h2 className="editorial-heading text-4xl sm:text-5xl text-[#FFF8E8] font-bold tracking-tight">
            What You&apos;re Building
          </h2>
        </motion.div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {cards.map((card, i) => (
            <motion.div
              key={card.title}
              className="rounded-2xl border border-[#185338] bg-[#073523] p-8 lg:p-10 transition-all duration-200 hover:border-[#F6BE2C]/40 hover:translate-y-[-2px] shadow-lg shadow-black/20"
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="mb-6 flex h-14 w-14 items-center justify-center text-[#F6BE2C]">
                <card.icon className="h-10 w-10" />
              </div>
              <h3 className="editorial-heading text-2xl text-[#FFF8E8] font-bold">
                {card.title}
              </h3>
              <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-[#EDE3C9] font-normal">
                {card.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Decorative Portuguese / Goan mosaic tile border strip */}
      <TropicalPattern className="h-9 w-full border-t border-b border-[#041E15]" />
    </section>
  );
}
