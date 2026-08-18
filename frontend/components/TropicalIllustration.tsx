"use client";

export default function TropicalIllustration() {
  return (
    <div className="relative w-full overflow-hidden select-none pointer-events-none">
      <svg
        viewBox="0 0 1000 480"
        className="w-full h-auto drop-shadow-2xl"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <linearGradient id="panoSky" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#052E1E" />
            <stop offset="60%" stopColor="#083E29" />
            <stop offset="100%" stopColor="#0B4B32" />
          </linearGradient>

          <linearGradient id="panoSea" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#09442C" />
            <stop offset="50%" stopColor="#0B5637" />
            <stop offset="100%" stopColor="#042C1D" />
          </linearGradient>

          <linearGradient id="panoSun" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFF275" />
            <stop offset="100%" stopColor="#F6BE2C" />
          </linearGradient>

          <filter id="panoGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="8" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* ── BACKGROUND SKY ── */}
        <rect width="1000" height="480" fill="url(#panoSky)" />

        {/* ── DISTANT MOUNTAINS & HILLS ── */}
        <path
          d="M0 160 Q120 140 240 165 T480 160 T720 165 T1000 155 L1000 170 L0 170 Z"
          fill="#063221"
        />
        <path
          d="M160 162 Q230 148 300 162 Z"
          fill="#09422C"
        />
        <path
          d="M700 162 Q770 145 850 162 Z"
          fill="#09422C"
        />

        {/* ── RADIATING GOLDEN SUN RAYS ── */}
        <g stroke="#F6BE2C" strokeWidth="2.8" strokeLinecap="round" opacity="0.95">
          {/* Left Rays */}
          <line x1="360" y1="130" x2="310" y2="90" />
          <line x1="410" y1="110" x2="380" y2="60" />
          <line x1="460" y1="95" x2="445" y2="40" />
          {/* Center Vertical Ray */}
          <line x1="500" y1="90" x2="500" y2="25" />
          {/* Right Rays */}
          <line x1="540" y1="95" x2="555" y2="40" />
          <line x1="590" y1="110" x2="620" y2="60" />
          <line x1="640" y1="130" x2="690" y2="90" />
        </g>

        {/* ── CENTRAL GOLDEN SUN ── */}
        <circle cx="500" cy="162" r="85" fill="#F6BE2C" opacity="0.2" filter="url(#panoGlow)" />
        <path
          d="M420 162 A 80 80 0 0 1 580 162 Z"
          fill="url(#panoSun)"
          stroke="#F6BE2C"
          strokeWidth="2"
        />

        {/* ── EMERALD SEA ── */}
        <rect x="0" y="162" width="1000" height="95" fill="url(#panoSea)" />

        {/* Fishing boat on water */}
        <g transform="translate(195, 172)">
          <path d="M0 10 L25 10 L30 18 L-5 18 Z" fill="#042216" stroke="#0E4E34" strokeWidth="1" />
          <rect x="5" y="4" width="12" height="6" fill="#FFFDF8" />
          <line x1="12" y1="4" x2="12" y2="0" stroke="#0E4E34" strokeWidth="1.5" />
        </g>

        {/* Sun Wave Reflections on Sea */}
        <g stroke="#F6BE2C" strokeWidth="3" strokeLinecap="round">
          <line x1="445" y1="170" x2="555" y2="170" />
          <line x1="430" y1="178" x2="570" y2="178" strokeWidth="3.5" />
          <line x1="420" y1="187" x2="580" y2="187" strokeWidth="4" />
          <line x1="435" y1="197" x2="565" y2="197" strokeWidth="3.5" />
          <line x1="455" y1="207" x2="545" y2="207" strokeWidth="3" />
          <line x1="470" y1="216" x2="530" y2="216" strokeWidth="2.5" />
          <line x1="480" y1="225" x2="520" y2="225" strokeWidth="2" />
        </g>

        {/* Water wave texture lines */}
        <g stroke="#0E5E41" strokeWidth="2" opacity="0.6">
          <line x1="60" y1="185" x2="180" y2="185" />
          <line x1="280" y1="195" x2="380" y2="195" />
          <line x1="620" y1="190" x2="740" y2="190" />
          <line x1="820" y1="182" x2="940" y2="182" />
        </g>

        {/* ── BEACH SHORELINE & WAVES ── */}
        <path
          d="M0 240 Q150 230 300 242 T600 245 T900 238 T1000 242 L1000 480 L0 480 Z"
          fill="#FFFDF8"
        />
        {/* Foamy wave border lines */}
        <path
          d="M0 240 Q150 230 300 242 T600 245 T900 238 T1000 242"
          stroke="#073B26"
          strokeWidth="3.5"
          fill="none"
        />
        <path
          d="M0 248 Q140 238 290 250 T590 252 T890 246 T1000 250"
          stroke="#0A4D32"
          strokeWidth="2"
          fill="none"
        />

        {/* ── BEACH UMBRELLAS & LOUNGERS ── */}
        {/* Umbrella 1 (Left) */}
        <g transform="translate(170, 240)">
          <line x1="30" y1="20" x2="35" y2="65" stroke="#2C1802" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M0 25 Q30 0 60 25 Q45 28 30 26 Q15 28 0 25 Z" fill="#F6BE2C" stroke="#2C1802" strokeWidth="2" />
          <path d="M15 26 L30 0 L0 25 Z" fill="#FFFDF8" />
          <path d="M45 26 L30 0 L60 25 Z" fill="#FFFDF8" />
          <path d="M30 0 L30 26" stroke="#2C1802" strokeWidth="1.5" />
          {/* Loungers */}
          <line x1="8" y1="65" x2="35" y2="78" stroke="#1D4E35" strokeWidth="3" strokeLinecap="round" />
          <line x1="42" y1="68" x2="68" y2="78" stroke="#1D4E35" strokeWidth="3" strokeLinecap="round" />
        </g>

        {/* Umbrella 2 (Center-Left) */}
        <g transform="translate(315, 250)">
          <line x1="30" y1="20" x2="35" y2="65" stroke="#2C1802" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M0 25 Q30 0 60 25 Q45 28 30 26 Q15 28 0 25 Z" fill="#F6BE2C" stroke="#2C1802" strokeWidth="2" />
          <path d="M15 26 L30 0 L0 25 Z" fill="#FFFDF8" />
          <path d="M45 26 L30 0 L60 25 Z" fill="#FFFDF8" />
          <path d="M30 0 L30 26" stroke="#2C1802" strokeWidth="1.5" />
          {/* Loungers */}
          <line x1="8" y1="65" x2="35" y2="78" stroke="#1D4E35" strokeWidth="3" strokeLinecap="round" />
          <line x1="42" y1="68" x2="68" y2="78" stroke="#1D4E35" strokeWidth="3" strokeLinecap="round" />
        </g>

        {/* ── SURFBOARDS ON SHORE ── */}
        <g transform="translate(570, 255)">
          <path d="M8 0 C14 15, 16 55, 14 90 L2 90 C0 55, 2 15, 8 0 Z" fill="#FFFDF8" stroke="#073523" strokeWidth="2" />
          <line x1="8" y1="0" x2="8" y2="90" stroke="#1C7D47" strokeWidth="1.5" />

          <path d="M26 4 C32 18, 34 55, 32 90 L20 90 C18 55, 20 18, 26 4 Z" fill="#F6BE2C" stroke="#073523" strokeWidth="2" />
          <line x1="26" y1="4" x2="26" y2="90" stroke="#D49B0D" strokeWidth="1.5" />
        </g>

        {/* ── "GOA BEACH" SHACK ── */}
        <g transform="translate(640, 235)">
          {/* Roof */}
          <polygon points="-5,35 60,5 125,35" fill="#1C7D47" stroke="#073523" strokeWidth="2.5" />
          {/* Main Walls */}
          <rect x="5" y="35" width="110" height="75" fill="#FFFDF8" stroke="#073523" strokeWidth="2.5" />
          {/* Pink GOA BEACH Signboard */}
          <rect x="15" y="10" width="90" height="24" rx="2" fill="#E60067" stroke="#FFFDF8" strokeWidth="2" />
          <text x="60" y="26" fill="#FFFDF8" fontFamily="system-ui, sans-serif" fontWeight="900" fontSize="10" letterSpacing="1" textAnchor="middle">
            GOA BEACH
          </text>
          {/* Bar Opening / Counter */}
          <rect x="15" y="48" width="70" height="42" fill="#FFFDF8" stroke="#073523" strokeWidth="2" />
          {/* Bartender Silhouette */}
          <circle cx="50" cy="62" r="5" fill="#073523" />
          <path d="M42 78 C42 70, 58 70, 58 78 Z" fill="#073523" />
          {/* Bar Stools */}
          <line x1="28" y1="90" x2="28" y2="108" stroke="#073523" strokeWidth="2" />
          <ellipse cx="28" cy="90" rx="6" ry="2" fill="#073523" />
          <line x1="50" y1="90" x2="50" y2="108" stroke="#073523" strokeWidth="2" />
          <ellipse cx="50" cy="90" rx="6" ry="2" fill="#073523" />
          <line x1="72" y1="90" x2="72" y2="108" stroke="#073523" strokeWidth="2" />
          <ellipse cx="72" cy="90" rx="6" ry="2" fill="#073523" />
        </g>

        {/* ── FOREGROUND VILLAGE COTTAGES & ROOFS ── */}
        {/* Left Villa Roof */}
        <g transform="translate(-10, 310)">
          <polygon points="0,50 80,0 160,50" fill="#1C7D47" stroke="#073523" strokeWidth="3" />
          <g stroke="#0E4E34" strokeWidth="2">
            <line x1="20" y1="50" x2="80" y2="5" />
            <line x1="45" y1="50" x2="80" y2="10" />
            <line x1="115" y1="50" x2="80" y2="10" />
            <line x1="140" y1="50" x2="80" y2="5" />
          </g>
          <rect x="15" y="50" width="130" height="120" fill="#FFFDF8" stroke="#073523" strokeWidth="3" />
          {/* Windows with green trim */}
          <rect x="35" y="70" width="30" height="40" fill="#1C7D47" stroke="#073523" strokeWidth="2" />
          <rect x="85" y="70" width="30" height="40" fill="#1C7D47" stroke="#073523" strokeWidth="2" />
        </g>

        {/* Center-Left Villa */}
        <g transform="translate(180, 335)">
          <polygon points="-10,50 90,-5 190,50" fill="#1C7D47" stroke="#073523" strokeWidth="3" />
          <rect x="10" y="50" width="160" height="110" fill="#FFFDF8" stroke="#073523" strokeWidth="3" />
          {/* Yellow window shutters */}
          <rect x="35" y="75" width="22" height="32" fill="#F6BE2C" stroke="#073523" strokeWidth="2" />
          <rect x="65" y="75" width="22" height="32" fill="#F6BE2C" stroke="#073523" strokeWidth="2" />
        </g>

        {/* Center-Right Villa with striped awning */}
        <g transform="translate(600, 345)">
          <polygon points="-10,45 80,-5 170,45" fill="#1C7D47" stroke="#073523" strokeWidth="3" />
          <rect x="5" y="45" width="150" height="110" fill="#FFFDF8" stroke="#073523" strokeWidth="3" />
          {/* Yellow & White Striped Awning */}
          <path d="M15 80 L65 80 L60 95 L10 95 Z" fill="#F6BE2C" stroke="#073523" strokeWidth="2" />
          <line x1="25" y1="80" x2="20" y2="95" stroke="#FFFDF8" strokeWidth="5" />
          <line x1="45" y1="80" x2="40" y2="95" stroke="#FFFDF8" strokeWidth="5" />
        </g>

        {/* Right Villa with Pink Shutters */}
        <g transform="translate(800, 320)">
          <polygon points="-10,50 90,0 190,50" fill="#1C7D47" stroke="#073523" strokeWidth="3" />
          <rect x="10" y="50" width="160" height="120" fill="#FFFDF8" stroke="#073523" strokeWidth="3" />
          {/* Pink window shutters */}
          <rect x="35" y="75" width="28" height="48" fill="#E60067" stroke="#073523" strokeWidth="2" />
          <rect x="90" y="75" width="28" height="48" fill="#E60067" stroke="#073523" strokeWidth="2" />
        </g>

        {/* ── FRAMING PALM TREES (Left & Right) ── */}
        {/* Leftmost Tall Palm Tree */}
        <g transform="translate(0, 100)">
          <path d="M40 380 Q55 240 70 120 Q80 40 90 0" fill="none" stroke="#2C1802" strokeWidth="12" strokeLinecap="round" />
          {/* Fronds */}
          <g stroke="#073523" strokeWidth="3" fill="#1C7D47">
            <path d="M90 0 Q20 -30 -40 0 Q20 15 90 0 Z" fill="#2E9E5E" />
            <path d="M90 0 Q30 30 -20 80 Q40 50 90 0 Z" fill="#1C7D47" />
            <path d="M90 0 Q140 -40 200 -10 Q140 10 90 0 Z" fill="#2E9E5E" />
            <path d="M90 0 Q140 30 180 80 Q130 50 90 0 Z" fill="#1C7D47" />
            <path d="M90 0 Q90 -70 100 -100 Q95 -40 90 0 Z" fill="#38B36E" />
          </g>
        </g>

        {/* Rightmost Tall Palm Tree */}
        <g transform="translate(850, 100)">
          <path d="M90 380 Q75 240 60 120 Q50 40 40 0" fill="none" stroke="#2C1802" strokeWidth="12" strokeLinecap="round" />
          <g stroke="#073523" strokeWidth="3" fill="#1C7D47">
            <path d="M40 0 Q-30 -30 -90 0 Q-30 15 40 0 Z" fill="#2E9E5E" />
            <path d="M40 0 Q-20 30 -70 80 Q-10 50 40 0 Z" fill="#1C7D47" />
            <path d="M40 0 Q110 -40 170 -10 Q110 10 40 0 Z" fill="#2E9E5E" />
            <path d="M40 0 Q110 30 150 80 Q100 50 40 0 Z" fill="#1C7D47" />
            <path d="M40 0 Q40 -70 50 -100 Q45 -40 40 0 Z" fill="#38B36E" />
          </g>
        </g>

        {/* Center Palm Trees */}
        <g transform="translate(240, 240)">
          <path d="M30 180 Q35 100 40 40" fill="none" stroke="#2C1802" strokeWidth="7" strokeLinecap="round" />
          <g stroke="#073523" strokeWidth="2" fill="#1C7D47">
            <path d="M40 40 Q0 15 -30 35 Q10 45 40 40 Z" />
            <path d="M40 40 Q80 15 110 35 Q70 45 40 40 Z" />
            <path d="M40 40 Q40 -10 45 -25 Q42 10 40 40 Z" fill="#2E9E5E" />
          </g>
        </g>

        <g transform="translate(740, 220)">
          <path d="M30 180 Q35 100 40 40" fill="none" stroke="#2C1802" strokeWidth="7" strokeLinecap="round" />
          <g stroke="#073523" strokeWidth="2" fill="#1C7D47">
            <path d="M40 40 Q0 15 -30 35 Q10 45 40 40 Z" />
            <path d="M40 40 Q80 15 110 35 Q70 45 40 40 Z" />
            <path d="M40 40 Q40 -10 45 -25 Q42 10 40 40 Z" fill="#2E9E5E" />
          </g>
        </g>
      </svg>
    </div>
  );
}
