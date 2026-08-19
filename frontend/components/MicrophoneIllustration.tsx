export default function MicrophoneIllustration() {
  return (
    <div className="relative w-full max-w-md select-none">
      <svg
        viewBox="0 0 360 260"
        className="w-full h-auto drop-shadow-md"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Sound Waves radiating from mic */}
        {/* Left Waves (Yellow/Gold) */}
        <path
          d="M130 90 C110 90, 95 110, 95 130 C95 150, 110 170, 130 170"
          stroke="#F6BE2C"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M115 75 C85 75, 65 100, 65 130 C65 160, 85 185, 115 185"
          stroke="#F6BE2C"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* Right Waves (Yellow/Gold) */}
        <path
          d="M230 90 C250 90, 265 110, 265 130 C265 150, 250 170, 230 170"
          stroke="#F6BE2C"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <path
          d="M245 75 C275 75, 295 100, 295 130 C295 160, 275 185, 245 185"
          stroke="#F6BE2C"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* ── BROWSER / TERMINAL WINDOW CONTAINER ── */}
        <rect
          x="45"
          y="100"
          width="270"
          height="145"
          rx="12"
          fill="#FFFDF8"
          stroke="#073523"
          strokeWidth="2"
        />

        {/* Window Top Controls Header */}
        <rect x="45" y="100" width="270" height="28" rx="12" fill="#F4EAD4" />
        <rect x="45" y="116" width="270" height="12" fill="#F4EAD4" />
        <line x1="45" y1="128" x2="315" y2="128" stroke="#073523" strokeWidth="1.5" />

        {/* 3 Window Control Dots */}
        <circle cx="62" cy="114" r="3.5" fill="#E60067" />
        <circle cx="74" cy="114" r="3.5" fill="#F6BE2C" />
        <circle cx="86" cy="114" r="3.5" fill="#1C7D47" />

        {/* Mock Waveform Lines & UI Elements */}
        <rect x="65" y="145" width="230" height="24" rx="6" fill="#F7F0DD" stroke="#E5D7B5" strokeWidth="1" />
        {/* Search placeholder text bar */}
        <rect x="75" y="153" width="70" height="8" rx="4" fill="#073523" opacity="0.6" />

        {/* Result cards mock */}
        <rect x="65" y="180" width="105" height="48" rx="6" fill="#073523" fillOpacity="0.06" stroke="#E5D7B5" strokeWidth="1" />
        <rect x="75" y="190" width="60" height="6" rx="3" fill="#1C7D47" />
        <rect x="75" y="202" width="80" height="4" rx="2" fill="#8C7A58" opacity="0.5" />
        <rect x="75" y="210" width="70" height="4" rx="2" fill="#8C7A58" opacity="0.5" />

        <rect x="180" y="180" width="115" height="48" rx="6" fill="#F6BE2C" fillOpacity="0.1" stroke="#F6BE2C" strokeWidth="1" />
        <rect x="190" y="190" width="70" height="6" rx="3" fill="#E60067" />
        <rect x="190" y="202" width="90" height="4" rx="2" fill="#8C7A58" opacity="0.5" />
        <rect x="190" y="210" width="80" height="4" rx="2" fill="#8C7A58" opacity="0.5" />

        {/* ── RETRO GREEN MICROPHONE ── */}
        <g id="microphone" transform="translate(152, 20)">
          {/* Mic Capsule */}
          <rect
            x="8"
            y="10"
            width="40"
            height="65"
            rx="20"
            fill="#1C7D47"
            stroke="#073523"
            strokeWidth="3"
          />

          {/* Mic Grille Stripes */}
          <g stroke="#0E331E" strokeWidth="2">
            <line x1="14" y1="26" x2="42" y2="26" />
            <line x1="14" y1="36" x2="42" y2="36" />
            <line x1="14" y1="46" x2="42" y2="46" />
            <line x1="18" y1="56" x2="38" y2="56" />
          </g>

          {/* Chrome / Metal U-Mount Cradle */}
          <path
            d="M-2 42 C-2 78, 58 78, 58 42"
            fill="none"
            stroke="#073523"
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          {/* Stand Stem & Base */}
          <line x1="28" y1="72" x2="28" y2="95" stroke="#073523" strokeWidth="4" strokeLinecap="round" />
          <line x1="10" y1="95" x2="46" y2="95" stroke="#073523" strokeWidth="4.5" strokeLinecap="round" />
        </g>
      </svg>
    </div>
  );
}
