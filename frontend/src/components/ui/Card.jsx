export default function Card({
  children,
  className = "",
  hover = false,
  glass = true,
  padding = "p-6",
  onClick,
  ...props
}) {
  const Component = onClick ? "button" : "div";
  return (
    <Component
      onClick={onClick}
      type={onClick ? "button" : undefined}
      className={`
        rounded-2xl text-left w-full
        ${glass ? "glass-panel-strong" : "bg-surface-raised border border-border"}
        ${hover ? "transition-all duration-300 hover:shadow-elevated hover:-translate-y-0.5" : "shadow-card"}
        ${padding}
        ${className}
      `}
      {...props}
    >
      {children}
    </Component>
  );
}
