export default function Logo({ size = 40, className = "" }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#d97706" />
          <stop offset="50%" stopColor="#22d3ee" />
          <stop offset="100%" stopColor="#c084fc" />
        </linearGradient>
        <linearGradient id="logoInner" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#f0b429" />
          <stop offset="100%" stopColor="#67e8f9" />
        </linearGradient>
      </defs>
      <rect width="48" height="48" rx="14" fill="url(#logoGrad)" />
      <path
        d="M14 32V16l10 8 10-8v16"
        stroke="#04060f"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <circle cx="24" cy="14" r="3" fill="url(#logoInner)" />
      <circle cx="14" cy="32" r="2" fill="rgba(4,6,15,0.5)" />
      <circle cx="34" cy="32" r="2" fill="rgba(4,6,15,0.5)" />
      <circle cx="24" cy="24" r="2" fill="rgba(4,6,15,0.7)" />
    </svg>
  );
}
