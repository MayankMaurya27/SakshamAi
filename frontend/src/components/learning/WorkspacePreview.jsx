import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Brain,
  BookOpen,
  Accessibility,
  FileText,
  MessageSquare,
  CheckCircle2,
  ArrowRight,
} from "lucide-react";
import Badge from "../ui/Badge";

const tabs = [
  {
    id: "learn",
    icon: BookOpen,
    title: "Learn",
    heading: "Ask anything. Understand deeply.",
    description:
      "Upload your notes and ask curriculum-aware questions. Saksham delivers explanations tailored to your class, subject, and learning profile.",
    route: "/learn",
    cta: "Start Learning",
    preview: "learn",
  },
  {
    id: "quiz",
    icon: Brain,
    title: "Quiz",
    heading: "Practice with purpose.",
    description:
      "Generate MCQ quizzes from your study material. Get instant feedback and track your progress over time.",
    route: "/quiz",
    cta: "Take a Quiz",
    preview: "quiz",
  },
  {
    id: "accessibility",
    icon: Accessibility,
    title: "Accessibility",
    heading: "Built for every learner.",
    description:
      "Beginner-friendly, dyslexia-supportive, and visually accessible modes adapt content presentation without changing the knowledge.",
    route: "/accessibility",
    cta: "Explore Profiles",
    preview: "accessibility",
  },
  {
    id: "revision",
    icon: FileText,
    title: "Revision",
    heading: "Revise smarter, not harder.",
    description:
      "Generate summaries, simplified explanations, and Hindi translations to reinforce concepts before exams.",
    route: "/learn",
    cta: "Revise Now",
    preview: "revision",
  },
];

function LearnPreview() {
  return (
    <div className="space-y-3 p-4">
      <div className="flex items-center gap-2 text-xs text-ink-muted">
        <MessageSquare size={14} className="text-accent" />
        Class 8 · Science · Photosynthesis
      </div>
      <div className="bg-primary/8 rounded-xl p-3 text-sm text-ink-muted">
        What is photosynthesis and why is it important?
      </div>
      <div className="bg-surface-raised rounded-xl p-4 border border-border text-sm leading-relaxed text-ink">
        <span className="text-accent font-semibold">Saksham: </span>
        Photosynthesis is the process by which green plants use sunlight,
        water, and carbon dioxide to produce glucose and oxygen...
      </div>
    </div>
  );
}

function QuizPreview() {
  return (
    <div className="space-y-3 p-4">
      <div className="text-xs font-semibold text-primary">Question 2 of 5</div>
      {["Chlorophyll", "Oxygen", "Glucose", "Water"].map((opt, i) => (
        <div
          key={opt}
          className={`rounded-xl px-4 py-2.5 text-sm border ${
            i === 0
              ? "border-accent/50 bg-accent/10 text-ink font-medium"
              : "border-border bg-surface text-ink-muted"
          }`}
        >
          {String.fromCharCode(65 + i)}. {opt}
        </div>
      ))}
      <div className="flex items-center gap-2 text-xs text-success">
        <CheckCircle2 size={14} />
        Instant feedback enabled
      </div>
    </div>
  );
}

function AccessibilityPreview() {
  const modes = ["Beginner", "Dyslexia", "Visual"];
  return (
    <div className="p-4 space-y-3">
      <div className="flex gap-2 flex-wrap">
        {modes.map((m, i) => (
          <span
            key={m}
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              i === 1
                ? "bg-primary text-void"
                : "bg-surface border border-border text-ink-muted"
            }`}
          >
            {m}
          </span>
        ))}
      </div>
      <div className="bg-surface-raised rounded-xl p-4 border border-border text-sm leading-loose text-ink">
        Plants make food using sunlight. This process is called photosynthesis.
      </div>
      <div className="text-xs text-ink-muted flex items-center gap-2">
        <Accessibility size={14} className="text-accent" />
        Simplified · Larger spacing · Browser narration
      </div>
    </div>
  );
}

function RevisionPreview() {
  return (
    <div className="p-4 space-y-3">
      <div className="flex gap-2 flex-wrap">
        {["Summary", "Simplify", "Hindi"].map((t, i) => (
          <span
            key={t}
            className={`px-3 py-1 rounded-full text-xs font-semibold ${
              i === 0
                ? "bg-primary text-void"
                : "bg-surface border border-border text-ink-muted"
            }`}
          >
            {t}
          </span>
        ))}
      </div>
      <div className="bg-surface-raised rounded-xl p-4 border border-border text-sm text-ink leading-relaxed">
        <strong className="text-primary">Key Points:</strong>
        <ul className="mt-2 space-y-1 list-disc list-inside text-ink-muted">
          <li>Plants convert light energy to chemical energy</li>
          <li>Chlorophyll captures sunlight in leaves</li>
          <li>Oxygen is released as a byproduct</li>
        </ul>
      </div>
    </div>
  );
}

const previews = {
  learn: LearnPreview,
  quiz: QuizPreview,
  accessibility: AccessibilityPreview,
  revision: RevisionPreview,
};

export default function WorkspacePreview() {
  const [active, setActive] = useState(tabs[0]);
  const Preview = previews[active.preview];

  return (
    <section id="workspace" className="py-20 lg:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <Badge variant="neural">Learning Workspace</Badge>
          <h2 className="font-display text-4xl md:text-5xl text-ink mt-4">
            One platform, every learning mode
          </h2>
          <p className="mt-4 text-ink-muted text-lg">
            From deep understanding to quick revision — explore how Saksham
            supports your entire learning journey.
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-2 mt-12">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = active.id === tab.id;
            return (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActive(tab)}
                className={`
                  flex items-center gap-2 px-5 py-2.5 rounded-full text-sm font-semibold
                  transition-all duration-300 border focus-ring
                  ${
                    isActive
                      ? "bg-primary text-void border-primary shadow-amber"
                      : "bg-surface text-ink-muted border-border hover:border-accent/40"
                  }
                `}
              >
                <Icon size={16} />
                {tab.title}
              </button>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={active.id}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            transition={{ duration: 0.35 }}
            className="mt-10 neural-border rounded-3xl overflow-hidden shadow-elevated"
          >
            <div className="grid lg:grid-cols-2 glass-panel-strong">
              <div className="p-8 lg:p-12 flex flex-col justify-center">
                <p className="text-xs font-bold uppercase tracking-widest text-accent">
                  {active.title}
                </p>
                <h3 className="font-display text-3xl md:text-4xl text-ink mt-3 leading-tight">
                  {active.heading}
                </h3>
                <p className="mt-4 text-ink-muted leading-relaxed">
                  {active.description}
                </p>
                <Link
                  to={active.route}
                  className="mt-8 inline-flex items-center gap-2 text-primary font-semibold hover:text-accent transition-colors group"
                >
                  {active.cta}
                  <ArrowRight
                    size={18}
                    className="group-hover:translate-x-1 transition-transform"
                  />
                </Link>
              </div>

              <div className="bg-gradient-to-br from-surface via-surface-raised to-accent/5 min-h-[320px] lg:min-h-[400px] flex items-center border-t lg:border-t-0 lg:border-l border-border">
                <div className="w-full max-w-md mx-auto">
                  <div className="mx-4 rounded-2xl border border-border glass-panel overflow-hidden">
                    <div className="flex items-center gap-1.5 px-4 py-3 border-b border-border bg-surface/80">
                      <div className="w-2.5 h-2.5 rounded-full bg-error/60" />
                      <div className="w-2.5 h-2.5 rounded-full bg-primary/60" />
                      <div className="w-2.5 h-2.5 rounded-full bg-success/60" />
                      <span className="ml-2 text-xs text-ink-faint font-medium">
                        Saksham Workspace
                      </span>
                    </div>
                    <Preview />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </section>
  );
}
