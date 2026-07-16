import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircle2,
  XCircle,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  Brain,
  Target,
  Bookmark,
  Sparkles,
  Zap,
  Award,
  HelpCircle,
  TrendingUp,
  AlertTriangle,
} from "lucide-react";
import Button from "../ui/Button";
import Card from "../ui/Card";
import Badge from "../ui/Badge";
import { explainQuizBatch } from "../../services/learningApi";

const DIFFICULTY_COLORS = {
  Easy: "bg-success/15 text-success border-success/30",
  Medium: "bg-gold/15 text-gold border-gold/30",
  Hard: "bg-error/15 text-error border-error/30",
};

function ExplanationPanel({ explanation, index }) {
  const [expanded, setExpanded] = useState(true);

  if (!explanation) return null;

  const diffClass = DIFFICULTY_COLORS[explanation.difficulty] || DIFFICULTY_COLORS.Medium;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="mt-4"
    >
      <div className="rounded-xl border border-border bg-surface-raised/50 overflow-hidden">
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-surface/40 transition-colors focus-ring rounded-t-xl"
          aria-expanded={expanded}
          aria-controls={`explanation-${index}`}
        >
          <span className="flex items-center gap-2 text-sm font-semibold text-accent">
            <Lightbulb size={16} />
            Detailed Explanation
          </span>
          {expanded ? <ChevronUp size={16} className="text-ink-muted" /> : <ChevronDown size={16} className="text-ink-muted" />}
        </button>

        <AnimatePresence>
          {expanded && (
            <motion.div
              id={`explanation-${index}`}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="px-4 pb-4 space-y-3"
              role="region"
              aria-label={`Explanation for question ${index + 1}`}
            >
              {/* Status + Difficulty badges */}
              <div className="flex flex-wrap gap-2 pt-1">
                <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold border ${
                  explanation.is_correct
                    ? "bg-success/15 text-success border-success/30"
                    : "bg-error/15 text-error border-error/30"
                }`}>
                  {explanation.is_correct ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                  {explanation.is_correct ? "Correct!" : "Incorrect"}
                </span>
                <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold border ${diffClass}`}>
                  <Target size={12} />
                  {explanation.difficulty || "Medium"}
                </span>
                {explanation.topic && (
                  <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-neural/15 text-neural border border-neural/30">
                    <Bookmark size={12} />
                    {explanation.topic}
                  </span>
                )}
              </div>

              {/* Why Correct */}
              <div className="p-3 rounded-lg bg-success/5 border border-success/15">
                <p className="text-xs font-bold text-success uppercase tracking-wider mb-1 flex items-center gap-1.5">
                  <CheckCircle2 size={13} /> Why Correct
                </p>
                <p className="text-sm text-ink leading-relaxed">{explanation.why_correct}</p>
              </div>

              {/* Why Wrong Options */}
              {explanation.why_wrong && Object.keys(explanation.why_wrong).length > 0 && (
                <div className="p-3 rounded-lg bg-error/5 border border-error/15">
                  <p className="text-xs font-bold text-error uppercase tracking-wider mb-2 flex items-center gap-1.5">
                    <XCircle size={13} /> Why Other Options Are Wrong
                  </p>
                  <div className="space-y-1.5">
                    {Object.entries(explanation.why_wrong).map(([letter, reason]) => (
                      reason && (
                        <p key={letter} className="text-sm text-ink-muted leading-relaxed">
                          <span className="font-bold text-error/80 mr-1">{letter}.</span>
                          {reason}
                        </p>
                      )
                    ))}
                  </div>
                </div>
              )}

              {/* Easy Explanation */}
              {explanation.easy_explanation && (
                <div className="p-3 rounded-lg bg-accent/5 border border-accent/15">
                  <p className="text-xs font-bold text-accent uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Sparkles size={13} /> Simple Explanation
                  </p>
                  <p className="text-sm text-ink leading-relaxed">{explanation.easy_explanation}</p>
                </div>
              )}

              {/* Two-column grid for compact items */}
              <div className="grid sm:grid-cols-2 gap-3">
                {/* Real-World Example */}
                {explanation.real_world_example && (
                  <div className="p-3 rounded-lg bg-gold/5 border border-gold/15">
                    <p className="text-xs font-bold text-gold uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <Zap size={13} /> Real-World Example
                    </p>
                    <p className="text-sm text-ink leading-relaxed">{explanation.real_world_example}</p>
                  </div>
                )}

                {/* Memory Trick */}
                {explanation.memory_trick && (
                  <div className="p-3 rounded-lg bg-neural/5 border border-neural/15">
                    <p className="text-xs font-bold text-neural uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <Brain size={13} /> Memory Trick
                    </p>
                    <p className="text-sm text-ink leading-relaxed">{explanation.memory_trick}</p>
                  </div>
                )}

                {/* Common Misconception */}
                {explanation.common_misconception && (
                  <div className="p-3 rounded-lg bg-error/5 border border-error/10">
                    <p className="text-xs font-bold text-error/80 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <AlertTriangle size={13} /> Common Mistake
                    </p>
                    <p className="text-sm text-ink leading-relaxed">{explanation.common_misconception}</p>
                  </div>
                )}

                {/* Related Concept */}
                {explanation.related_concept && (
                  <div className="p-3 rounded-lg bg-primary/5 border border-primary/15">
                    <p className="text-xs font-bold text-primary uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <TrendingUp size={13} /> Related Concept
                    </p>
                    <p className="text-sm text-ink leading-relaxed">{explanation.related_concept}</p>
                  </div>
                )}
              </div>

              {/* Follow-up Challenge */}
              {explanation.follow_up_question && (
                <div className="p-3 rounded-lg bg-accent/8 border border-accent/20">
                  <p className="text-xs font-bold text-accent uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <HelpCircle size={13} /> Challenge Yourself
                  </p>
                  <p className="text-sm text-ink leading-relaxed italic">{explanation.follow_up_question}</p>
                </div>
              )}

              {/* Study Suggestion */}
              {explanation.study_suggestion && (
                <div className="p-3 rounded-lg bg-surface border border-border">
                  <p className="text-xs font-bold text-primary uppercase tracking-wider mb-1 flex items-center gap-1.5">
                    <Award size={13} /> Study Tip
                  </p>
                  <p className="text-sm text-ink-muted leading-relaxed">{explanation.study_suggestion}</p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

function ScoreSummary({ score, total, explanations }) {
  const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
  const isExcellent = percentage >= 80;
  const isGood = percentage >= 50;

  // Aggregate weak topics from incorrect answers
  const weakTopics = [];
  if (explanations) {
    explanations.forEach((exp) => {
      if (exp && !exp.is_correct && exp.topic) {
        if (!weakTopics.includes(exp.topic)) weakTopics.push(exp.topic);
      }
    });
  }

  return (
    <Card className={`${isExcellent ? "bg-success/8 border-success/25" : isGood ? "bg-gold/8 border-gold/25" : "bg-error/8 border-error/25"}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className={`text-sm font-semibold ${isExcellent ? "text-success" : isGood ? "text-gold" : "text-error"}`}>
            {isExcellent ? "🎉 Excellent!" : isGood ? "👍 Good Effort!" : "📚 Keep Practicing!"}
          </p>
          <p className="text-2xl font-bold text-ink mt-1">
            {score} / {total} correct
          </p>
          {weakTopics.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1.5">
              <span className="text-xs text-ink-muted font-medium">Revise:</span>
              {weakTopics.slice(0, 3).map((topic) => (
                <span key={topic} className="text-xs px-2 py-0.5 rounded-full bg-error/10 text-error border border-error/20 font-medium">
                  {topic}
                </span>
              ))}
            </div>
          )}
        </div>
        <div className="text-right">
          <div className={`text-4xl font-black ${isExcellent ? "text-success" : isGood ? "text-gold" : "text-error"}`}>
            {percentage}%
          </div>
          {/* Confidence meter */}
          <div className="mt-2 w-24 h-2 rounded-full bg-surface overflow-hidden">
            <motion.div
              className={`h-full rounded-full ${isExcellent ? "bg-success" : isGood ? "bg-gold" : "bg-error"}`}
              initial={{ width: 0 }}
              animate={{ width: `${percentage}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
          <p className="text-xs text-ink-muted mt-1">Confidence</p>
        </div>
      </div>
    </Card>
  );
}

function QuestionProgressBar({ total, answered, submitted }) {
  if (!total) return null;
  const pct = Math.round((answered / total) * 100);

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between text-xs text-ink-muted mb-1.5">
        <span>{submitted ? "Review your answers" : `${answered}/${total} answered`}</span>
        <span>{pct}%</span>
      </div>
      <div className="w-full h-1.5 rounded-full bg-surface overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${submitted ? "bg-accent" : "bg-primary"}`}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
    </div>
  );
}

export default function QuizPanel({
  quiz,
  selectedAnswers,
  setSelectedAnswers,
  quizSubmitted,
  onSubmit,
  score,
  topic,
  subject,
  classLevel,
}) {
  const [explanations, setExplanations] = useState([]);
  const [explanationsLoading, setExplanationsLoading] = useState(false);

  if (quiz.length === 0) {
    return (
      <Card className="text-center py-12">
        <div className="flex flex-col items-center gap-3">
          <Brain size={40} className="text-ink-muted opacity-40" />
          <p className="text-ink-muted">
            Generate a quiz using the learning tools panel.
          </p>
        </div>
      </Card>
    );
  }

  const answeredCount = Object.keys(selectedAnswers).length;
  const allAnswered = quiz.every((_, i) => selectedAnswers[i]);

  const handleSubmit = async () => {
    onSubmit();

    // Fetch explanations in background
    setExplanationsLoading(true);
    try {
      const results = await explainQuizBatch(quiz, selectedAnswers, topic, subject, classLevel);
      setExplanations(results);
    } catch (err) {
      console.warn("Could not load explanations:", err.message);
      setExplanations([]);
    } finally {
      setExplanationsLoading(false);
    }
  };

  return (
    <div className="space-y-6" role="region" aria-label="Quiz questions">
      <QuestionProgressBar
        total={quiz.length}
        answered={answeredCount}
        submitted={quizSubmitted}
      />

      {quizSubmitted && score !== null && (
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <ScoreSummary score={score} total={quiz.length} explanations={explanations} />
        </motion.div>
      )}

      {quiz.map((q, index) => {
        const explanation = explanations[index] || null;

        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
          >
            <Card padding="p-5">
              <p className="font-semibold text-ink mb-4" id={`question-${index}`}>
                <span className="text-accent mr-2">{index + 1}.</span>
                {q.question}
              </p>
              <div className="space-y-2" role="radiogroup" aria-labelledby={`question-${index}`}>
                {["A", "B", "C", "D"].map((option) => {
                  const isSelected = selectedAnswers[index] === option;
                  const isCorrect = option === q.correct_answer;
                  const showResult = quizSubmitted;

                  let style =
                    "border-border bg-surface hover:border-accent/40 cursor-pointer";
                  if (showResult && isCorrect) {
                    style = "border-success/50 bg-success/10";
                  } else if (showResult && isSelected && !isCorrect) {
                    style = "border-error/50 bg-error/10";
                  } else if (isSelected) {
                    style = "border-accent/50 bg-accent/10";
                  }

                  return (
                    <label
                      key={option}
                      className={`flex items-center gap-3 p-3.5 rounded-xl border transition-all ${style}`}
                    >
                      <input
                        type="radio"
                        disabled={quizSubmitted}
                        name={`question-${index}`}
                        value={option}
                        checked={isSelected}
                        onChange={() =>
                          setSelectedAnswers((current) => ({
                            ...current,
                            [index]: option,
                          }))
                        }
                        className="accent-accent"
                        aria-label={`Option ${option}: ${q.options[option]}`}
                      />
                      <span className="text-sm text-ink flex-1">
                        <span className="font-semibold text-primary mr-2">
                          {option}.
                        </span>
                        {q.options[option]}
                      </span>
                      {showResult && isCorrect && (
                        <CheckCircle2 size={18} className="text-success shrink-0" aria-label="Correct answer" />
                      )}
                      {showResult && isSelected && !isCorrect && (
                        <XCircle size={18} className="text-error shrink-0" aria-label="Wrong answer" />
                      )}
                    </label>
                  );
                })}
              </div>

              {/* Rich explanation panel after submission */}
              <AnimatePresence>
                {quizSubmitted && explanation && (
                  <ExplanationPanel explanation={explanation} index={index} />
                )}
              </AnimatePresence>

              {quizSubmitted && explanationsLoading && !explanation && (
                <div className="mt-4 flex items-center gap-2 text-sm text-ink-muted">
                  <div className="w-4 h-4 rounded-full border-2 border-accent/40 border-t-accent animate-spin" />
                  Loading explanation...
                </div>
              )}
            </Card>
          </motion.div>
        );
      })}

      {!quizSubmitted && (
        <Button
          onClick={handleSubmit}
          disabled={!allAnswered}
          className="w-full sm:w-auto"
        >
          Submit Quiz ({answeredCount}/{quiz.length} answered)
        </Button>
      )}
    </div>
  );
}
