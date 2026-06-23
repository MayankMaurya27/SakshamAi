import { motion, AnimatePresence } from "framer-motion";
import {
  Play,
  Pause,
  Square,
  Volume2,
  VolumeX,
  Gauge,
} from "lucide-react";

const RATE_OPTIONS = [0.75, 1, 1.25, 1.5];

function Waveform({ active }) {
  return (
    <div className="flex items-end gap-[3px] h-5" aria-hidden="true">
      {[0, 1, 2, 3, 4].map((i) => (
        <motion.span
          key={i}
          className="w-[3px] rounded-full bg-accent origin-bottom"
          animate={
            active
              ? { scaleY: [0.35, 1, 0.5, 0.9, 0.35] }
              : { scaleY: 0.25 }
          }
          transition={
            active
              ? { duration: 0.9, repeat: Infinity, delay: i * 0.12 }
              : { duration: 0.2 }
          }
          style={{ height: "100%" }}
        />
      ))}
    </div>
  );
}

export default function AudioPlayer({
  text = "",
  status,
  volume,
  rate,
  onToggle,
  onStop,
  onVolumeChange,
  onRateChange,
  label = "Read Aloud",
  compact = false,
}) {
  const isPlaying = status === "playing";
  const isPaused = status === "paused";
  const isActive = isPlaying || isPaused;
  const hasText = Boolean(text?.trim());
  const muted = volume === 0;

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => onToggle(text)}
          disabled={!hasText}
          aria-label={isPlaying ? "Pause" : isPaused ? "Resume" : "Play"}
          className="
            w-9 h-9 rounded-xl flex items-center justify-center
            bg-accent/15 text-accent border border-accent/25
            hover:bg-accent/25 transition-all
            disabled:opacity-40 disabled:cursor-not-allowed focus-ring
          "
        >
          {isPlaying ? <Pause size={16} /> : <Play size={16} className="ml-0.5" />}
        </button>
        {isActive && (
          <button
            type="button"
            onClick={onStop}
            aria-label="Stop"
            className="w-9 h-9 rounded-xl flex items-center justify-center text-ink-muted hover:text-error transition-colors focus-ring"
          >
            <Square size={14} />
          </button>
        )}
      </div>
    );
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="neural-border rounded-2xl overflow-hidden"
      >
        <div className="bg-surface-raised/90 backdrop-blur-xl p-4 sm:p-5">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-3 min-w-0">
              <div
                className={`
                  w-10 h-10 rounded-xl flex items-center justify-center shrink-0
                  ${isActive ? "bg-accent/20 text-accent" : "bg-primary/15 text-primary"}
                `}
              >
                <Volume2 size={18} />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-ink truncate">{label}</p>
                <p className="text-xs text-ink-muted">
                  {isPlaying
                    ? "Speaking…"
                    : isPaused
                      ? "Paused"
                      : "Browser voice · no server needed"}
                </p>
              </div>
            </div>
            <Waveform active={isPlaying} />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => onToggle(text)}
                disabled={!hasText}
                aria-label={isPlaying ? "Pause" : isPaused ? "Resume" : "Play"}
                className="
                  w-11 h-11 rounded-xl flex items-center justify-center
                  bg-gradient-to-br from-primary to-primary-dark text-void
                  shadow-amber hover:scale-105 active:scale-95
                  transition-all disabled:opacity-40 disabled:cursor-not-allowed focus-ring
                "
              >
                {isPlaying ? (
                  <Pause size={20} />
                ) : (
                  <Play size={20} className="ml-0.5" />
                )}
              </button>

              <button
                type="button"
                onClick={onStop}
                disabled={!isActive}
                aria-label="Stop"
                className="
                  w-11 h-11 rounded-xl flex items-center justify-center
                  border border-border-strong text-ink-muted
                  hover:border-error/40 hover:text-error
                  transition-all disabled:opacity-30 disabled:cursor-not-allowed focus-ring
                "
              >
                <Square size={16} />
              </button>
            </div>

            <div className="flex items-center gap-2 flex-1 min-w-[120px]">
              <button
                type="button"
                onClick={() => onVolumeChange(muted ? 0.85 : 0)}
                aria-label={muted ? "Unmute" : "Mute"}
                className="text-ink-muted hover:text-accent transition-colors focus-ring rounded-lg p-1"
              >
                {muted ? <VolumeX size={16} /> : <Volume2 size={16} />}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={volume}
                onChange={(e) => onVolumeChange(parseFloat(e.target.value))}
                aria-label="Volume"
                className="range-slider flex-1"
              />
              <span className="text-xs text-ink-faint w-8 text-right tabular-nums">
                {Math.round(volume * 100)}%
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Gauge size={14} className="text-ink-faint shrink-0" />
              <div className="flex gap-1">
                {RATE_OPTIONS.map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => onRateChange(r)}
                    className={`
                      px-2 py-1 rounded-lg text-xs font-semibold transition-all focus-ring
                      ${
                        rate === r
                          ? "bg-accent/20 text-accent border border-accent/30"
                          : "text-ink-muted hover:text-ink border border-transparent"
                      }
                    `}
                  >
                    {r}×
                  </button>
                ))}
              </div>
            </div>
          </div>

          {!hasText && (
            <p className="mt-3 text-xs text-ink-faint">
              Generate content first to enable narration.
            </p>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
