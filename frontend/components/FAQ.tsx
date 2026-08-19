"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const faqs = [
  {
    question: "Who can participate in Hacker House Goa?",
    answer:
      "Developers, ML engineers, and builders who can demonstrate strong technical skills through our open trials. Both students and professionals are welcome to apply.",
  },
  {
    question: "How does the selection process work?",
    answer:
      "Selection happens in phases: open trials, alpha shortlist based on performance, beta review of technical depth and portfolio, and final onsite interviews for team fit.",
  },
  {
    question: "Can I start working on my project before the event?",
    answer:
      "Yes. Open trials are designed for you to start building early. Submissions for the voice-enabled RAG task are evaluated on their own merit before the onsite event.",
  },
  {
    question: "Is there a registration fee?",
    answer:
      "Registration for open trials is free. Selected participants receive details about onsite logistics separately.",
  },
  {
    question: "How are teams formed?",
    answer:
      "You can apply solo or as a pre-formed team. During selection, we may suggest team combinations based on complementary skills.",
  },
];

function FAQIllustration() {
  return (
    <div className="relative w-full overflow-hidden select-none pointer-events-none flex justify-center items-center">
      <svg
        viewBox="0 0 540 480"
        className="w-full h-auto drop-shadow-xl"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <linearGradient id="faqHouseRoof" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#D35400" />
            <stop offset="100%" stopColor="#9C3B00" />
          </linearGradient>

          <linearGradient id="surfboardGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#FFE066" />
            <stop offset="50%" stopColor="#F6BE2C" />
            <stop offset="100%" stopColor="#E5A610" />
          </linearGradient>
        </defs>

        {/* ── SANDY PATH & SHORELINE ── */}
        <path
          d="M200 480 C260 450, 320 460, 380 435 C420 418, 480 430, 540 420 L540 480 Z"
          fill="#F5E8C9"
        />
        <path
          d="M240 480 C280 465, 330 470, 380 455 C430 440, 480 450, 540 445 L540 480 Z"
          fill="#EEDDB3"
        />
        {/* Winding sandy pathway leading to villa */}
        <path
          d="M260 480 Q320 440 370 420 Q400 405 420 395 L440 405 Q410 420 360 450 Q300 475 280 480 Z"
          fill="#E5D1A2"
          stroke="#C5B182"
          strokeWidth="1.5"
        />

        {/* ── COLONIAL TWO-STORY GOAN VILLA ── */}
        <g id="faq-villa" transform="translate(370, 230)">
          {/* Shadow */}
          <ellipse cx="65" cy="180" rx="65" ry="10" fill="#041E15" opacity="0.6" />

          {/* Ground Floor Wall */}
          <rect x="10" y="80" width="110" height="95" fill="#FFFDF8" stroke="#1B3E2E" strokeWidth="2.5" />
          {/* Ground Floor Verandah Pillars */}
          <rect x="10" y="80" width="110" height="15" fill="#F4EAD4" stroke="#1B3E2E" strokeWidth="2" />
          <line x1="25" y1="95" x2="25" y2="175" stroke="#1B3E2E" strokeWidth="3" />
          <line x1="65" y1="95" x2="65" y2="175" stroke="#1B3E2E" strokeWidth="3" />
          <line x1="105" y1="95" x2="105" y2="175" stroke="#1B3E2E" strokeWidth="3" />

          {/* Ground Floor Window (Right) */}
          <rect x="75" y="115" width="25" height="38" fill="#F6BE2C" stroke="#1B3E2E" strokeWidth="2" />
          <g stroke="#2C1802" strokeWidth="1.2">
            <line x1="77" y1="124" x2="98" y2="124" />
            <line x1="77" y1="133" x2="98" y2="133" />
            <line x1="77" y1="142" x2="98" y2="142" />
          </g>

          {/* Ground Floor Doorway (Left) */}
          <rect x="32" y="115" width="26" height="60" fill="#0D3522" stroke="#1B3E2E" strokeWidth="2" />
          <line x1="45" y1="115" x2="45" y2="175" stroke="#1B3E2E" strokeWidth="1.5" />

          {/* First Floor Wall */}
          <rect x="15" y="15" width="100" height="68" fill="#FFFDF8" stroke="#1B3E2E" strokeWidth="2.5" />

          {/* First Floor Balcony Railing */}
          <rect x="12" y="58" width="106" height="24" fill="#F9F6EE" stroke="#1B3E2E" strokeWidth="2" />
          <g stroke="#1B3E2E" strokeWidth="2">
            <line x1="22" y1="58" x2="22" y2="82" />
            <line x1="34" y1="58" x2="34" y2="82" />
            <line x1="46" y1="58" x2="46" y2="82" />
            <line x1="58" y1="58" x2="58" y2="82" />
            <line x1="70" y1="58" x2="70" y2="82" />
            <line x1="82" y1="58" x2="82" y2="82" />
            <line x1="94" y1="58" x2="94" y2="82" />
            <line x1="106" y1="58" x2="106" y2="82" />
          </g>

          {/* First Floor Shuttered Windows */}
          <rect x="25" y="22" width="24" height="34" fill="#F6BE2C" stroke="#1B3E2E" strokeWidth="2" />
          <rect x="80" y="22" width="24" height="34" fill="#F6BE2C" stroke="#1B3E2E" strokeWidth="2" />
          {/* Slats */}
          <g stroke="#2C1802" strokeWidth="1.2">
            <line x1="27" y1="30" x2="47" y2="30" />
            <line x1="27" y1="38" x2="47" y2="38" />
            <line x1="27" y1="46" x2="47" y2="46" />
            <line x1="82" y1="30" x2="102" y2="30" />
            <line x1="82" y1="38" x2="102" y2="38" />
            <line x1="82" y1="46" x2="102" y2="46" />
          </g>

          {/* Terracotta Clay Tiled Roof */}
          <polygon points="0,18 65,-25 130,18" fill="url(#faqHouseRoof)" stroke="#2C1802" strokeWidth="2.5" />
          <g stroke="#662500" strokeWidth="2">
            <line x1="10" y1="18" x2="65" y2="-20" />
            <line x1="25" y1="18" x2="65" y2="-15" />
            <line x1="40" y1="18" x2="65" y2="-10" />
            <line x1="55" y1="18" x2="65" y2="-5" />
            <line x1="75" y1="18" x2="65" y2="-5" />
            <line x1="90" y1="18" x2="65" y2="-10" />
            <line x1="105" y1="18" x2="65" y2="-15" />
            <line x1="120" y1="18" x2="65" y2="-20" />
          </g>

          {/* Tropical Plants at House Base */}
          <ellipse cx="5" cy="175" rx="16" ry="12" fill="#1C7D47" stroke="#0E331E" strokeWidth="1.5" />
          <ellipse cx="125" cy="175" rx="18" ry="14" fill="#1C7D47" stroke="#0E331E" strokeWidth="1.5" />
        </g>

        {/* ── YELLOW SURFBOARD (Foreground, Planted in sand) ── */}
        <g id="surfboard" transform="translate(300, 270)">
          {/* Drop shadow on sand */}
          <ellipse cx="14" cy="165" rx="16" ry="4" fill="#BFAF82" opacity="0.8" />

          {/* Upright Curved Surfboard */}
          <path
            d="M14 0 C24 25, 28 85, 24 165 L4 165 C0 85, 4 25, 14 0 Z"
            fill="url(#surfboardGrad)"
            stroke="#2B1A04"
            strokeWidth="2.5"
          />

          {/* Center Stringer Stripe */}
          <line x1="14" y1="4" x2="14" y2="164" stroke="#D49B0D" strokeWidth="2" />
          {/* Side Contour highlights */}
          <path d="M8 20 Q6 85 8 155" stroke="#FFFDF8" strokeWidth="1.5" opacity="0.6" fill="none" />

          {/* Floral / Graphic pattern on surfboard */}
          <circle cx="14" cy="50" r="4" fill="#E60067" />
          <circle cx="14" cy="80" r="4" fill="#E60067" />
        </g>

        {/* ── TALL COCONUT PALM TREES ── */}
        {/* Palm 1: Framing Right Edge */}
        <g id="faq-palm-right">
          <path
            d="M485 480 Q475 360 460 240 Q445 140 430 80"
            fill="none"
            stroke="#5A3518"
            strokeWidth="11"
            strokeLinecap="round"
          />
          {/* Bark texture */}
          <g stroke="#351B06" strokeWidth="2">
            <line x1="478" y1="420" x2="489" y2="420" />
            <line x1="470" y1="360" x2="480" y2="360" />
            <line x1="461" y1="300" x2="471" y2="300" />
            <line x1="450" y1="230" x2="459" y2="230" />
            <line x1="440" y1="160" x2="448" y2="160" />
            <line x1="428" y1="100" x2="435" y2="100" />
          </g>

          {/* Palm Fronds Crown */}
          <g stroke="#0E331E" strokeWidth="2.5" fill="#1C7D47">
            <path d="M430 80 Q370 45 310 70 Q370 95 430 80 Z" fill="#2E9E5E" />
            <path d="M430 80 Q360 90 300 135 Q365 135 430 80 Z" fill="#208B4F" />
            <path d="M430 80 Q360 140 320 200 Q380 170 430 80 Z" fill="#176E3B" />
            <path d="M430 80 Q430 20 440 0 Q440 50 430 80 Z" fill="#38B36E" />
            <path d="M430 80 Q485 30 535 45 Q495 75 430 80 Z" fill="#2E9E5E" />
            <path d="M430 80 Q500 70 540 120 Q490 125 430 80 Z" fill="#208B4F" />
          </g>
        </g>

        {/* Palm 2: Middle Palm */}
        <g id="faq-palm-middle">
          <path
            d="M375 480 Q365 370 355 260 Q345 170 330 110"
            fill="none"
            stroke="#533118"
            strokeWidth="9"
            strokeLinecap="round"
          />
          <g stroke="#0E331E" strokeWidth="2.2" fill="#1C7D47">
            <path d="M330 110 Q280 80 230 100 Q280 120 330 110 Z" fill="#2E9E5E" />
            <path d="M330 110 Q270 120 220 160 Q275 160 330 110 Z" fill="#208B4F" />
            <path d="M330 110 Q335 50 340 30 Q340 80 330 110 Z" fill="#38B36E" />
            <path d="M330 110 Q380 65 425 80 Q390 105 330 110 Z" fill="#2E9E5E" />
            <path d="M330 110 Q390 100 430 145 Q385 150 330 110 Z" fill="#208B4F" />
          </g>
        </g>
      </svg>
    </div>
  );
}

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  return (
    <section className="bg-[#073523] py-16 lg:py-24 border-t border-[#144833]/80" id="faq">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
          
          {/* ── LEFT COLUMN: ACCORDION ── */}
          <div className="lg:col-span-7 flex flex-col">
            
            {/* FAQ Header with ornamental divider */}
            <div className="mb-8">
              <h2 className="editorial-heading text-4xl sm:text-5xl lg:text-6xl uppercase tracking-wide text-[#F6BE2C] font-bold">
                FAQS
              </h2>
              {/* Gold glyph ornamental divider line matching reference */}
              <div className="mt-3 flex items-center gap-2 text-[#F6BE2C] text-xs font-serif opacity-85 select-none">
                <span>✦</span>
                <span>◆</span>
                <span>✦</span>
                <span>◆</span>
                <span>✦</span>
                <div className="h-px w-24 bg-[#F6BE2C]/60" />
              </div>
            </div>

            {/* Accordion Cards (Pill / Rounded Border Boxes) */}
            <div className="space-y-3">
              {faqs.map((faq, i) => {
                const isOpen = openIndex === i;
                return (
                  <div
                    key={faq.question}
                    className={`rounded-2xl border transition-all duration-200 overflow-hidden ${
                      isOpen
                        ? "border-[#F6BE2C]/70 bg-[#05281A]"
                        : "border-[#1D5E3F] bg-[#073523] hover:border-[#F6BE2C]/40"
                    }`}
                  >
                    <button
                      type="button"
                      className="w-full flex items-center justify-between gap-4 px-6 py-4 sm:py-5 text-left focus:outline-none"
                      onClick={() => setOpenIndex(isOpen ? null : i)}
                      aria-expanded={isOpen}
                    >
                      <span className="text-[15px] sm:text-[16px] font-medium leading-snug text-[#FFF8E8]">
                        {faq.question}
                      </span>
                      
                      {/* Plus icon inside circular badge */}
                      <span
                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border transition-all duration-200 ${
                          isOpen
                            ? "border-[#F6BE2C] bg-[#F6BE2C] text-[#073523]"
                            : "border-[#F6BE2C] text-[#F6BE2C] bg-transparent"
                        }`}
                      >
                        <svg
                          width="14"
                          height="14"
                          viewBox="0 0 14 14"
                          fill="none"
                          xmlns="http://www.w3.org/2000/svg"
                          className="stroke-current"
                        >
                          <line x1="7" y1="2" x2="7" y2="12" strokeWidth="2" strokeLinecap="round" />
                          {!isOpen && (
                            <line x1="2" y1="7" x2="12" y2="7" strokeWidth="2" strokeLinecap="round" />
                          )}
                        </svg>
                      </span>
                    </button>

                    <AnimatePresence initial={false}>
                      {isOpen && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: "auto", opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          transition={{ duration: 0.25, ease: "easeInOut" }}
                        >
                          <p className="px-6 pb-5 pt-1 text-sm leading-relaxed text-[#EDE3C9] font-normal border-t border-[#144833]/60">
                            {faq.answer}
                          </p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── RIGHT COLUMN: GOA VILLA & SURFBOARD ARTWORK ── */}
          <div className="lg:col-span-5 flex justify-center lg:justify-end">
            <FAQIllustration />
          </div>

        </div>
      </div>
    </section>
  );
}
