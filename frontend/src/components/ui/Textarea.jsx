export default function Textarea({
  label,
  value,
  onChange,
  placeholder,
  rows = 4,
  className = "",
  ...props
}) {
  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label className="block text-sm font-semibold text-ink">
          {label}
        </label>
      )}
      <textarea
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        rows={rows}
        className="
          w-full resize-none
          bg-surface-raised border border-border-strong
          rounded-2xl px-5 py-4
          text-ink placeholder:text-ink-faint
          focus-ring transition-colors
          hover:border-accent/40
          leading-relaxed
        "
        {...props}
      />
    </div>
  );
}
