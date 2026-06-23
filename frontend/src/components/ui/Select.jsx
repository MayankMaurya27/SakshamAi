import { ChevronDown } from "lucide-react";

export default function Select({
  label,
  value,
  onChange,
  options = [],
  placeholder = "Select...",
  className = "",
  disabled = false,
}) {
  return (
    <div className={`space-y-1.5 ${className}`}>
      {label && (
        <label className="block text-xs font-semibold uppercase tracking-wider text-ink-muted">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          value={value}
          onChange={onChange}
          disabled={disabled}
          className="
            w-full appearance-none
            bg-surface-raised border border-border-strong
            rounded-xl px-4 py-3 pr-10
            text-sm font-medium text-ink
            focus-ring transition-colors
            hover:border-accent/40
            disabled:opacity-50 disabled:cursor-not-allowed
          "
        >
          {options.length === 0 && (
            <option value="">{placeholder}</option>
          )}
          {options.map((opt) => {
            const val = typeof opt === "object" ? opt.value : opt;
            const labelText = typeof opt === "object" ? opt.label : opt;
            return (
              <option key={val} value={val}>
                {labelText}
              </option>
            );
          })}
        </select>
        <ChevronDown
          size={16}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-muted pointer-events-none"
        />
      </div>
    </div>
  );
}
