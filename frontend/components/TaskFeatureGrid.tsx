"use client";

import {
  IconMicrophone,
  IconNodes,
  IconSpeed,
  IconChart,
  IconHarness,
  IconShield,
} from "./LineIcons";

const features = [
  {
    icon: IconMicrophone,
    title: "Speak the question",
    description: "Real voice-to-text input,\nnot typed",
  },
  {
    icon: IconNodes,
    title: "Engineered Retrieval",
    description: "Multiple chunking strategies,\nnot one naive split",
  },
  {
    icon: IconSpeed,
    title: "Blazing Fast",
    description: "Full pipeline\nunder 200ms",
  },
  {
    icon: IconChart,
    title: "Benchmarked",
    description: "P50 / P70 / P100 latency,\nbenchmarked across real queries",
  },
  {
    icon: IconHarness,
    title: "Real Harness",
    description: "Retries, structured I/O,\nerror recovery",
  },
  {
    icon: IconShield,
    title: "Guardrails",
    description: "Knows when\nnot to answer",
  },
];

export default function TaskFeatureGrid() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {features.map((feature) => (
        <div
          key={feature.title}
          className="rounded-xl border border-[#E5D7B5] bg-[#FFFDF8] p-6 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:border-[#1C7D47]/40"
        >
          <div className="mb-4 text-[#073523]">
            <feature.icon className="h-7 w-7" />
          </div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-[#073523]">
            {feature.title}
          </h4>
          <p className="mt-2 whitespace-pre-line text-xs leading-relaxed text-[#567364] font-medium">
            {feature.description}
          </p>
        </div>
      ))}
    </div>
  );
}
