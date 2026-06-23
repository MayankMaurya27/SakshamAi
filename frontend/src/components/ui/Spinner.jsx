import { Loader2 } from "lucide-react";

export default function Spinner({ size = "md", className = "" }) {
  const sizes = { sm: 16, md: 24, lg: 36 };
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Loader2 size={sizes[size]} className="animate-spin text-accent" />
    </div>
  );
}

export function LoadingState({ message = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-4">
      <Spinner size="lg" />
      <p className="text-sm text-ink-muted font-medium">{message}</p>
    </div>
  );
}
