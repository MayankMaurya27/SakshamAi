import { Link } from "react-router-dom";
import { Loader2 } from "lucide-react";

const variants = {
  primary:
    "bg-gradient-to-br from-primary to-primary-dark text-void shadow-amber hover:shadow-glow hover:brightness-110 active:scale-[0.98]",
  secondary:
    "bg-surface-raised text-ink border border-border-strong hover:border-accent/50 hover:text-accent shadow-soft",
  accent:
    "bg-accent/15 text-accent border border-accent/30 hover:bg-accent/25 hover:shadow-glow active:scale-[0.98]",
  ghost:
    "bg-transparent text-ink-muted hover:text-primary hover:bg-primary/8",
  danger:
    "bg-error/10 text-error border border-error/25 hover:bg-error/18",
};

const sizes = {
  sm: "px-3.5 py-2 text-sm gap-1.5 rounded-lg",
  md: "px-5 py-2.5 text-sm gap-2 rounded-xl",
  lg: "px-7 py-3.5 text-base gap-2.5 rounded-xl",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  className = "",
  icon: Icon,
  to,
  href,
  target,
  rel,
  ...props
}) {
  const classes = `
    inline-flex items-center justify-center font-semibold
    transition-all duration-200 focus-ring
    disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
    ${variants[variant]} ${sizes[size]} ${className}
  `;

  const content = (
    <>
      {loading ? (
        <Loader2 size={size === "sm" ? 14 : 18} className="animate-spin" />
      ) : Icon ? (
        <Icon size={size === "sm" ? 14 : 18} />
      ) : null}
      {children}
    </>
  );

  if (to) {
    return (
      <Link to={to} className={classes} {...props}>
        {content}
      </Link>
    );
  }

  if (href) {
    return (
      <a
        href={href}
        target={target}
        rel={rel || (target === "_blank" ? "noopener noreferrer" : undefined)}
        className={classes}
        {...props}
      >
        {content}
      </a>
    );
  }

  return (
    <button
      type="button"
      disabled={disabled || loading}
      className={classes}
      {...props}
    >
      {content}
    </button>
  );
}
