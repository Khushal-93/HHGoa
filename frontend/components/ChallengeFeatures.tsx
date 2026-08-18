"use client";

import { motion } from "framer-motion";
import {
  IconMicrophone,
  IconNodes,
  IconSpeed,
  IconChart,
  IconShield,
} from "./LineIcons";

const features = [
  {
    icon: IconMicrophone,
    title: "Voice In",
    description: "Speak your question\nreal voice input",
  },
  {
    icon: IconNodes,
    title: "Engineered Retrieval",
    description: "Multiple chunking\nstrategies, not naive split",
  },
  {
    icon: IconSpeed,
    title: "Blazing Fast",
    description: "Full pipeline\nunder 200ms",
  },
  {
    icon: IconChart,
    title: "Benchmarked",
    description: "P50 / P70 / P100 latency,\non real queries",
  },
  {
    icon: IconShield,
    title: "Guardrails",
    description: "Knows when\nnot to answer",
  },
];

export default function ChallengeFeatures() {
  return (
    <section className="bg-[#F7F0DD] paper-texture relative py-16 lg:py-24 border-t border-[#E5D7B5]">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <p className="label-upper mb-3 text-[#FF007A] font-bold tracking-[0.22em]">
            The Challenge
          </p>
          <h2 className="editorial-heading text-3xl sm:text-4xl lg:text-5xl text-[#073523] font-bold">
            Build a Voice-to-Answer RAG Pipeline
          </h2>
        </motion.div>

        <div className="mt-14 grid grid-cols-2 gap-8 sm:grid-cols-3 lg:grid-cols-5">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              className="flex flex-col items-center text-center group"
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
            >
              {/* Minimal Line Icon without heavy container */}
              <div className="mb-4 flex h-14 w-14 items-center justify-center text-[#073523] transition-transform group-hover:scale-110">
                <feature.icon className="h-10 w-10 stroke-[1.8]" />
              </div>
              <h3 className="text-xs font-bold uppercase tracking-wider text-[#073523]">
                {feature.title}
              </h3>
              <p className="mt-2 whitespace-pre-line text-xs leading-relaxed text-[#2A5240] font-medium">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
