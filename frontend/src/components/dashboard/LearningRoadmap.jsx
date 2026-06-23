import { CheckCircle2, Circle } from "lucide-react";

export default function LearningRoadmap({ chapters, selectedChapter }) {
  if (chapters.length === 0) {
    return (
      <div className="py-8 text-center text-ink-muted text-sm">
        No chapters available for this subject
      </div>
    );
  }

  const selectedIndex = chapters.findIndex(
    (ch) => ch.chapter_title === selectedChapter,
  );

  return (
    <div className="space-y-0">
      {chapters.map((chapter, index) => {
        const isPast = selectedIndex >= 0 && index < selectedIndex;
        const isCurrent = chapter.chapter_title === selectedChapter;
        const isLast = index === chapters.length - 1;

        return (
          <div key={chapter.chapter_id} className="flex gap-4">
            <div className="flex flex-col items-center">
              <div
                className={`
                  w-8 h-8 rounded-full flex items-center justify-center shrink-0
                  ${
                    isCurrent
                      ? "bg-primary text-void shadow-amber"
                      : isPast
                        ? "bg-success/15 text-success"
                        : "bg-surface border border-border text-ink-faint"
                  }
                `}
              >
                {isPast ? (
                  <CheckCircle2 size={16} />
                ) : isCurrent ? (
                  <span className="text-xs font-bold">{index + 1}</span>
                ) : (
                  <Circle size={14} />
                )}
              </div>
              {!isLast && (
                <div
                  className={`w-0.5 flex-1 min-h-[32px] ${
                    isPast ? "bg-success/30" : "bg-border"
                  }`}
                />
              )}
            </div>
            <div className={`pb-6 ${isLast ? "pb-0" : ""}`}>
              <p
                className={`text-sm font-semibold ${
                  isCurrent ? "text-accent" : isPast ? "text-primary" : "text-ink-muted"
                }`}
              >
                Chapter {index + 1}
              </p>
              <p
                className={`mt-0.5 text-sm ${
                  isCurrent ? "text-primary font-medium" : "text-ink-muted"
                }`}
              >
                {chapter.chapter_title}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
