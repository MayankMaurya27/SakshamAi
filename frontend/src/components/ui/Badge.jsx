export default function Badge({
  children,
  variant = "default",
  className = "",
}) {
  const variants = {
    default: "bg-primary/8 text-primary border-primary/15",
    primary: "bg-primary/8 text-primary border-primary/15",
    accent: "bg-accent/10 text-accent border-accent/20",
    neural: "bg-neural/10 text-neural border-neural/20",
    gold: "bg-gold/10 text-gold border-gold/20",
    success: "bg-success/10 text-success border-success/20",
  };

  return (
    <span
      className={`
        inline-flex items-center gap-1.5
        px-3 py-1 rounded-full
        text-xs font-semibold tracking-wide
        border
        ${variants[variant]}
        ${className}
      `}
    >
      {children}
    </span>
  );
}
