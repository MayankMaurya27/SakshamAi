import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  GraduationCap,
  Lightbulb,
  Zap,
  TrendingUp,
  AlertTriangle,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Sparkles,
} from "lucide-react";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import useProgressStore from "../../store/progressStore";

function WeakTopicAlert({ weakTopics }) {
  if (!weakTopics || weakTopics.length === 0) return null;

  return (
    <div className="p-3 rounded-xl bg-error/5 border border-error/15">
      <p className="text-xs font-bold text-error uppercase tracking-wider mb-2 flex items-center gap-1.5">
        <AlertTriangle size={13} />
        Focus Areas
      </p>
      <div className="space-y-1.5">
        {weakTopics.slice(0, 3).map((t) => (
          <div key={t.topic} className="flex items-center justify-between">
            <span className="text-sm text-ink">{t.topic}</span>
            <span className="text-xs font-bold text-error">{t.percentage}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function StudySuggestion({ topicMastery, weakTopics }) {
  if (topicMastery.length === 0) {
    return (
      <div className="p-3 rounded-xl bg-accent/5 border border-accent/15">
        <p className="text-xs font-bold text-accent uppercase tracking-wider mb-1 flex items-center gap-1.5">
          <Lightbulb size={13} />
          Getting Started
        </p>
        <p className="text-sm text-ink-muted">
          Take your first quiz to get personalized study recommendations!
        </p>
      </div>
    );
  }

  const bestTopic = topicMastery[0];
  const suggestion = weakTopics.length > 0
    ? `Focus on ${weakTopics[0].topic} — you scored ${weakTopics[0].percentage}%. Try a quiz on this topic.`
    : bestTopic
      ? `Great work on ${bestTopic.topic} (${bestTopic.percentage}%)! Try a harder challenge.`
      : "Keep practicing with different chapters!";

  return (
    <div className="p-3 rounded-xl bg-accent/5 border border-accent/15">
      <p className="text-xs font-bold text-accent uppercase tracking-wider mb-1 flex items-center gap-1.5">
        <Lightbulb size={13} />
        Study Suggestion
      </p>
      <p className="text-sm text-ink-muted">{suggestion}</p>
    </div>
  );
}

function NextTopicRecommendation({ topicMastery, currentChapter }) {
  // Suggest the topic with lowest mastery that isn't the current one
  const nextTopic = topicMastery
    .filter((t) => t.topic !== currentChapter && t.percentage < 80)
    .sort((a, b) => a.percentage - b.percentage)[0];

  if (!nextTopic) return null;

  return (
    <div className="p-3 rounded-xl bg-neural/5 border border-neural/15">
      <p className="text-xs font-bold text-neural uppercase tracking-wider mb-1 flex items-center gap-1.5">
        <TrendingUp size={13} />
        Next Recommended
      </p>
      <p className="text-sm text-ink">
        {nextTopic.topic}{" "}
        <span className="text-ink-muted">({nextTopic.percentage}% mastery)</span>
      </p>
    </div>
  );
}

export default function StudyCoach({ currentChapter, onSimplify, hasQuestion }) {
  const [expanded, setExpanded] = useState(true);
  const {
    getWeakTopics,
    getTopicMastery,
    getExamReadiness,
    getLevel,
    currentStreak,
    totalXP,
  } = useProgressStore();

  const weakTopics = getWeakTopics();
  const topicMastery = getTopicMastery();
  const readiness = getExamReadiness();
  const level = getLevel();

  return (
    <Card className="h-fit">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between text-left focus-ring rounded-lg"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-neural/15 flex items-center justify-center">
            <GraduationCap size={18} className="text-neural" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-primary">AI Study Coach</h3>
            <p className="text-xs text-ink-muted">Personalized guidance</p>
          </div>
        </div>
        {expanded ? (
          <ChevronUp size={16} className="text-ink-muted" />
        ) : (
          <ChevronDown size={16} className="text-ink-muted" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="mt-4 space-y-3"
          >
            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-2">
              <div className="text-center p-2 rounded-lg bg-surface">
                <p className="text-lg font-bold text-primary">{level.level}</p>
                <p className="text-[10px] text-ink-muted font-medium">{level.title}</p>
              </div>
              <div className="text-center p-2 rounded-lg bg-surface">
                <p className="text-lg font-bold text-gold">{currentStreak}</p>
                <p className="text-[10px] text-ink-muted font-medium">Streak</p>
              </div>
              <div className="text-center p-2 rounded-lg bg-surface">
                <p className="text-lg font-bold text-accent">{readiness}%</p>
                <p className="text-[10px] text-ink-muted font-medium">Ready</p>
              </div>
            </div>

            <StudySuggestion topicMastery={topicMastery} weakTopics={weakTopics} />
            <WeakTopicAlert weakTopics={weakTopics} />
            <NextTopicRecommendation topicMastery={topicMastery} currentChapter={currentChapter} />

            {/* Quick actions */}
            {hasQuestion && onSimplify && (
              <button
                type="button"
                onClick={onSimplify}
                className="w-full flex items-center gap-2 p-3 rounded-xl bg-gold/5 border border-gold/15 text-sm font-medium text-gold hover:bg-gold/10 transition-colors focus-ring"
              >
                <Sparkles size={14} />
                Explain Like I'm 10
              </button>
            )}

            <div className="pt-2 border-t border-border">
              <p className="text-[10px] text-ink-faint text-center">
                Powered by your learning data · {totalXP} XP earned
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
}
