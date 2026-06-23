import { CheckCircle2, XCircle } from "lucide-react";
import Button from "../ui/Button";
import Card from "../ui/Card";

export default function QuizPanel({
  quiz,
  selectedAnswers,
  setSelectedAnswers,
  quizSubmitted,
  onSubmit,
  score,
}) {
  if (quiz.length === 0) {
    return (
      <Card className="text-center py-12">
        <p className="text-ink-muted">
          Generate a quiz using the learning tools panel.
        </p>
      </Card>
    );
  }

  const allAnswered = quiz.every((_, i) => selectedAnswers[i]);

  return (
    <div className="space-y-6">
      {quizSubmitted && score !== null && (
        <Card className="bg-accent/8 border-accent/25">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-accent">Quiz Complete</p>
              <p className="text-2xl font-bold text-ink mt-1">
                {score} / {quiz.length} correct
              </p>
            </div>
            <div className="text-4xl font-black text-primary">
              {Math.round((score / quiz.length) * 100)}%
            </div>
          </div>
        </Card>
      )}

      {quiz.map((q, index) => (
        <Card key={index} padding="p-5">
          <p className="font-semibold text-ink mb-4">
            <span className="text-accent mr-2">{index + 1}.</span>
            {q.question}
          </p>
          <div className="space-y-2">
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
                  />
                  <span className="text-sm text-ink flex-1">
                    <span className="font-semibold text-primary mr-2">
                      {option}.
                    </span>
                    {q.options[option]}
                  </span>
                  {showResult && isCorrect && (
                    <CheckCircle2 size={18} className="text-success shrink-0" />
                  )}
                  {showResult && isSelected && !isCorrect && (
                    <XCircle size={18} className="text-error shrink-0" />
                  )}
                </label>
              );
            })}
          </div>
        </Card>
      ))}

      {!quizSubmitted && (
        <Button
          onClick={onSubmit}
          disabled={!allAnswered}
          className="w-full sm:w-auto"
        >
          Submit Quiz
        </Button>
      )}
    </div>
  );
}
