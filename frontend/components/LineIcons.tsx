export function IconMicrophone({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="12" y="4" width="8" height="14" rx="4" />
      <path d="M8 14v2a8 8 0 0016 0v-2" />
      <line x1="16" y1="24" x2="16" y2="28" />
      <line x1="12" y1="28" x2="20" y2="28" />
    </svg>
  );
}

export function IconNodes({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <circle cx="16" cy="8" r="3" />
      <circle cx="8" cy="24" r="3" />
      <circle cx="24" cy="24" r="3" />
      <line x1="16" y1="11" x2="8" y2="21" />
      <line x1="16" y1="11" x2="24" y2="21" />
      <line x1="11" y1="24" x2="21" y2="24" />
    </svg>
  );
}

export function IconSpeed({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 20a12 12 0 0124 0" />
      <line x1="16" y1="20" x2="22" y2="10" />
      <circle cx="16" cy="20" r="2" fill="currentColor" />
      <text x="8" y="14" fontSize="5" fill="currentColor" stroke="none">200</text>
    </svg>
  );
}

export function IconChart({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <line x1="4" y1="28" x2="28" y2="28" />
      <rect x="6" y="18" width="5" height="10" />
      <rect x="14" y="12" width="5" height="16" />
      <rect x="22" y="6" width="5" height="22" />
    </svg>
  );
}

export function IconShield({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M16 4L6 8v8c0 6 4.5 11.5 10 13 5.5-1.5 10-7 10-13V8L16 4z" />
      <path d="M12 16l3 3 6-7" />
    </svg>
  );
}

export function IconWaveform({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M4 16 Q8 8 12 16 T20 16 T28 16" />
      <path d="M4 22 Q8 14 12 22 T20 22 T28 22" opacity="0.5" />
    </svg>
  );
}

export function IconRAG({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="4" y="6" width="10" height="12" rx="1" />
      <rect x="18" y="6" width="10" height="12" rx="1" />
      <circle cx="16" cy="24" r="4" />
      <line x1="9" y1="18" x2="13" y2="22" />
      <line x1="23" y1="18" x2="19" y2="22" />
    </svg>
  );
}

export function IconHarness({ className = "w-8 h-8" }: { className?: string }) {
  return (
    <svg viewBox="0 0 32 32" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <rect x="6" y="8" width="20" height="16" rx="2" />
      <path d="M10 14h12M10 18h8" />
      <path d="M22 22l4 4" />
    </svg>
  );
}

export function IconDownload({ className = "w-5 h-5" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} fill="none" stroke="currentColor" strokeWidth="1.5">
      <path d="M12 3v12M8 11l4 4 4-4" />
      <path d="M4 19h16" />
    </svg>
  );
}
