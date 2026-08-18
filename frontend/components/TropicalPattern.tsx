export default function TropicalPattern({ className = "h-8" }: { className?: string }) {
  return (
    <div
      className={`w-full overflow-hidden select-none ${className}`}
      aria-hidden="true"
    >
      <svg
        viewBox="0 0 1200 32"
        preserveAspectRatio="none"
        className="h-full w-full"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="goan-azulejo-strip"
            x="0"
            y="0"
            width="64"
            height="32"
            patternUnits="userSpaceOnUse"
          >
            {/* Background strip */}
            <rect width="64" height="32" fill="#042216" />
            <line x1="0" y1="0" x2="64" y2="0" stroke="#E60067" strokeWidth="1.5" />
            <line x1="0" y1="32" x2="64" y2="32" stroke="#E60067" strokeWidth="1.5" />

            {/* Rosette 1 (Center) */}
            <circle cx="16" cy="16" r="11" fill="#E60067" />
            <circle cx="16" cy="16" r="8" fill="#F6BE2C" />
            <circle cx="16" cy="16" r="5" fill="#1C7D47" />
            <circle cx="16" cy="16" r="2.5" fill="#FFFDF8" />
            {/* Petals */}
            <circle cx="16" cy="7" r="2.5" fill="#FFFDF8" />
            <circle cx="16" cy="25" r="2.5" fill="#FFFDF8" />
            <circle cx="7" cy="16" r="2.5" fill="#FFFDF8" />
            <circle cx="25" cy="16" r="2.5" fill="#FFFDF8" />

            {/* Geometric Diamond Divider */}
            <polygon points="32,6 38,16 32,26 26,16" fill="#F6BE2C" stroke="#042216" strokeWidth="1" />
            <circle cx="32" cy="16" r="2" fill="#E60067" />

            {/* Rosette 2 (Right) */}
            <circle cx="48" cy="16" r="11" fill="#1C7D47" />
            <circle cx="48" cy="16" r="8" fill="#E60067" />
            <circle cx="48" cy="16" r="5" fill="#F6BE2C" />
            <circle cx="48" cy="16" r="2.5" fill="#042216" />
            <circle cx="48" cy="7" r="2.5" fill="#F6BE2C" />
            <circle cx="48" cy="25" r="2.5" fill="#F6BE2C" />
            <circle cx="39" cy="16" r="2.5" fill="#F6BE2C" />
            <circle cx="57" cy="16" r="2.5" fill="#F6BE2C" />

            {/* Border dots */}
            <circle cx="0" cy="16" r="2" fill="#F6BE2C" />
            <circle cx="64" cy="16" r="2" fill="#F6BE2C" />
          </pattern>
        </defs>
        <rect width="1200" height="32" fill="url(#goan-azulejo-strip)" />
      </svg>
    </div>
  );
}
