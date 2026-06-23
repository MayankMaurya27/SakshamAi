import {
  Brain,
  FileText,
  BookOpen,
  Languages,
} from "lucide-react";
import Card from "../ui/Card";

const tools = [
  {
    id: "quiz",
    label: "Generate Quiz",
    desc: "5 MCQs from chapter",
    icon: Brain,
    action: "quiz",
  },
  {
    id: "summary",
    label: "Summarize",
    desc: "Chapter revision notes",
    icon: FileText,
    action: "summary",
  },
  {
    id: "simplify",
    label: "Simplify",
    desc: "Easier explanation",
    icon: BookOpen,
    action: "simplify",
    needsAnswer: false,
    needsQuestionOrAnswer: true,
  },
  {
    id: "hindi",
    label: "Hindi",
    desc: "Hinenglish translation",
    icon: Languages,
    action: "hindi",
    needsAnswer: true,
  },
];

export default function LearningTools({
  onQuiz,
  onSummary,
  onSimplify,
  onHindi,
  quizLoading,
  summaryLoading,
  simplifyLoading,
  hindiLoading,
  hasAnswer,
  hasQuestion,
}) {
  const handlers = {
    quiz: onQuiz,
    summary: onSummary,
    simplify: onSimplify,
    hindi: onHindi,
  };

  const loadings = {
    quiz: quizLoading,
    summary: summaryLoading,
    simplify: simplifyLoading,
    hindi: hindiLoading,
  };

  return (
    <Card className="sticky top-24 h-fit">
      <h2 className="text-lg font-bold text-primary">Learning Tools</h2>
      <p className="text-sm text-ink-muted mt-1">
        Transform content with one tap
      </p>

      <div className="mt-5 space-y-2">
        {tools.map((tool) => {
          const Icon = tool.icon;
          const isLoading = loadings[tool.action];
          const disabled =
            (tool.needsAnswer && !hasAnswer) ||
            (tool.needsQuestionOrAnswer && !hasAnswer && !hasQuestion);

          return (
            <button
              key={tool.id}
              type="button"
              onClick={handlers[tool.action]}
              disabled={isLoading || disabled}
              title={disabled ? "Generate an answer first" : tool.desc}
              className="
                w-full flex items-center gap-3 px-4 py-3.5 rounded-xl
                border border-border bg-surface
                text-left transition-all duration-200
                hover:border-accent/40 hover:bg-accent/5
                disabled:opacity-40 disabled:cursor-not-allowed
                focus-ring group
              "
            >
              <div className="w-9 h-9 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0 group-hover:bg-accent/15 group-hover:text-accent transition-colors">
                <Icon size={17} />
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-ink">
                  {isLoading ? "Generating…" : tool.label}
                </p>
                <p className="text-xs text-ink-faint truncate">{tool.desc}</p>
              </div>
            </button>
          );
        })}
      </div>

      <p className="mt-4 text-xs text-ink-faint leading-relaxed">
        Audio narration runs in your browser — use the player below your answer
        for play, pause, volume & speed controls.
      </p>
    </Card>
  );
}
