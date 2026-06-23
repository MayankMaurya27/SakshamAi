import Badge from "./Badge";

export default function PageHeader({
  eyebrow,
  title,
  description,
  badge,
  children,
  align = "left",
}) {
  const alignClass = align === "center" ? "text-center items-center" : "text-left";

  return (
    <header className={`flex flex-col gap-4 ${alignClass}`}>
      {eyebrow && (
        <p className="text-xs font-bold uppercase tracking-[0.25em] text-accent">
          {eyebrow}
        </p>
      )}
      {badge && <Badge variant="neural">{badge}</Badge>}
      <h1 className="font-display text-4xl md:text-5xl lg:text-6xl text-ink leading-[1.1]">
        {title}
      </h1>
      {description && (
        <p className="text-lg text-ink-muted max-w-2xl leading-relaxed">
          {description}
        </p>
      )}
      {children}
    </header>
  );
}
