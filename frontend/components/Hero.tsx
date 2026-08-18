"use client";

import TropicalIllustration from "./TropicalIllustration";

export default function Hero() {
  return (
    <section className="relative w-full bg-[#073523] overflow-hidden flex flex-col justify-between pt-8 pb-0">
      
      {/* ── TOP HERO BRANDING (Exact Match to Reference Image) ── */}
      <div className="relative z-10 mx-auto w-full max-w-7xl px-6 lg:px-10 text-center flex flex-col items-center">
        
        {/* Giant HACKER [गोवा] HOUSE Display Typography */}
        <div className="relative inline-flex items-center justify-center my-4 select-none">
          
          {/* Main Title: HACKER HOUSE in Tall Condensed Serif Font */}
          <h1
            className="editorial-heading text-[4.2rem] sm:text-[6.5rem] md:text-[8.5rem] lg:text-[10.5rem] xl:text-[12rem] leading-[0.85] font-normal tracking-[-0.01em] uppercase text-[#F6BE2C] flex items-center justify-center gap-4 sm:gap-8"
            style={{
              fontFamily: "var(--font-cormorant), Georgia, serif",
              textShadow: "0 4px 20px rgba(0, 0, 0, 0.25)",
            }}
          >
            <span>HACKER</span>
            <span>HOUSE</span>
          </h1>

          {/* Superimposed Hot-Pink Devanagari "गोवा" Badge in Center */}
          <div
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-20 pointer-events-none"
            style={{
              transform: "translate(-50%, -46%) rotate(-3deg)",
            }}
          >
            <span
              className="text-[3.2rem] sm:text-[4.8rem] md:text-[6.4rem] lg:text-[8rem] xl:text-[9.5rem] font-black tracking-tight leading-none text-[#FF007A]"
              style={{
                fontFamily: "system-ui, -apple-system, sans-serif",
                textShadow:
                  "0 0 0 #F6BE2C, 2px 2px 0px #F6BE2C, -2px -2px 0px #F6BE2C, 2px -2px 0px #F6BE2C, -2px 2px 0px #F6BE2C, 0 6px 20px rgba(0,0,0,0.4)",
                WebkitTextStroke: "2px #F6BE2C",
              }}
            >
              गोवा
            </span>
          </div>
        </div>

        {/* Metadata Bar Under Title: GOA, INDIA • 28 - 31 OCT 2026 | 2:47 PM STUDIO */}
        <div className="w-full max-w-5xl flex items-center justify-between text-xs sm:text-sm font-bold tracking-[0.22em] text-[#EDE3C9] uppercase pt-2 pb-6 px-2 border-b border-[#144833]/40">
          <div className="flex items-center gap-3 text-[#EDE3C9]">
            <span>GOA, INDIA</span>
            <span className="text-[#F6BE2C] text-[10px]">●</span>
            <span>28 - 31 OCT 2026</span>
          </div>

          <div className="text-[#F6BE2C] tracking-[0.25em] font-extrabold">
            2:47 PM STUDIO
          </div>
        </div>
      </div>

      {/* ── PANORAMIC ILLUSTRATED SUNSET BEACH SCENE ── */}
      <div className="relative w-full mt-4 z-0">
        <TropicalIllustration />
      </div>
    </section>
  );
}
