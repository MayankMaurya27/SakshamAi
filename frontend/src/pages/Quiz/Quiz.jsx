import { useState } from "react";
import { motion } from "framer-motion";
import {
  Brain,
  BookOpen,
  Target,
  ChevronRight,
  Sparkles,
  AlertCircle,
  Zap,
  Flame,
} from "lucide-react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeader from "../../components/ui/PageHeader";
import Card from "../../components/ui/Card";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import { LoadingState } from "../../components/ui/Spinner";
import QuizPanel from "../../components/learning/QuizPanel";
import KnowledgeBackground from "../../components/background/KnowledgeBackground";
import { useDocuments, useCurriculum } from "../../hooks/useLearning";
import { generateQuiz, buildLearningPayload } from "../../services/learningApi";
import useProgressStore from "../../store/progressStore";

const quizModes = [
  {
    icon: BookOpen,
    title: "Curriculum Quiz",
    description: "Generate quizzes from your syllabus and chapters.",
    count: 5,
  },
  {
    icon: Brain,
    title: "Revision Quiz",
    description: "Quick revision before tests and examinations.",
    count: 5,
  },
  {
    icon: Target,
    title: "Chapter Challenge",
    description: "Focus on a specific topic or chapter.",
    count: 8,
  },
  {
    icon: Zap,
    title: "Quick Practice",
    description: "Fast 3-question warm-up to build momentum.",
    count: 3,
  },
  {
    icon: Flame,
    title: "Adaptive Challenge",
    description: "Difficulty adapts based on your performance history.",
    count: 10,
    adaptive: true,
  },
];

export default function Quiz() {
  const { documents, loading: docsLoading, error: docsError } = useDocuments();
  const curriculum = useCurriculum();
  const { questionsAnswered, getAverageScore, bestScore, quizAttempts } =
    useProgressStore();

  const [selectedDocument, setSelectedDocument] = useState("");
  const [source, setSource] = useState("saksham");
  const [error, setError] = useState("");
  const profile = "beginner";
  const [quiz, setQuiz] = useState([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [activeMode, setActiveMode] = useState(null);
  const recordQuizAttempt = useProgressStore((s) => s.recordQuizAttempt);

  const handleGenerate = async (mode) => {
    const docId = selectedDocument || documents[0]?.id;
    if (source === "document" && !docId) {
      setError("Please upload or select a document first.");
      return;
    }

    // Adaptive difficulty: adjust count based on past performance
    let questionCount = mode.count;
    if (mode.adaptive) {
      const avg = getAverageScore();
      if (avg >= 80) questionCount = 12;      // high performer → more challenge
      else if (avg >= 50) questionCount = 8;   // medium → standard
      else if (avg > 0) questionCount = 5;     // struggling → focused practice
      // avg === 0 means no history, use default
    }

    try {
      setQuizLoading(true);
      setError("");
      setActiveMode(mode.title);
      const questions = await generateQuiz({
        ...buildLearningPayload({
          source,
          documentId: docId,
          classLevel: curriculum.selectedClass,
          subject: curriculum.selectedSubject,
          chapter: curriculum.selectedChapter,
          profile,
        }),
        topic: curriculum.selectedChapter,
        question_count: questionCount,
      });
      setQuiz(questions);
      setSelectedAnswers({});
      setScore(null);
      setQuizSubmitted(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setQuizLoading(false);
    }
  };

  const submitQuiz = () => {
    let total = 0;
    quiz.forEach((q, index) => {
      if (selectedAnswers[index] === q.correct_answer) total++;
    });
    setScore(total);
    setQuizSubmitted(true);
    recordQuizAttempt({
      score: total,
      total: quiz.length,
      chapter: curriculum.selectedChapter,
      subject: curriculum.selectedSubject,
      classLevel: curriculum.selectedClass,
    });
  };

  if (docsLoading || curriculum.loading) {
    return (
      <MainLayout>
        <LoadingState message="Loading quiz center..." />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <KnowledgeBackground intensity="subtle" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <PageHeader
          eyebrow="Assessment Workspace"
          title="Quiz Center"
          description="Practice concepts, test understanding, and track your learning progress."
          align="center"
        />

        {(error || curriculum.error || docsError) && (
          <div className="mt-6 flex items-center gap-2 text-sm text-error bg-error/10 border border-error/20 rounded-xl px-4 py-3">
            <AlertCircle size={16} className="shrink-0" />
            {error || curriculum.error || docsError}
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-4 mt-12">
          {[
            { label: "Questions Attempted", value: questionsAnswered },
            { label: "Average Score", value: `${getAverageScore()}%` },
            { label: "Best Score", value: `${bestScore}%` },
          ].map((stat) => (
            <Card key={stat.label} className="text-center">
              <p className="text-sm text-ink-muted font-medium">{stat.label}</p>
              <p className="mt-2 text-3xl font-bold text-primary">{stat.value}</p>
            </Card>
          ))}
        </div>

        <Card className="mt-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <Select
              label="Quiz Source"
              value={source}
              onChange={(e) => {
                setSource(e.target.value);
                setError("");
              }}
              options={[
                { value: "saksham", label: "Saksham Curriculum" },
                { value: "document", label: "Uploaded Document" },
              ]}
            />
            <Select
              label="Class"
              value={curriculum.selectedClass}
              onChange={(e) => curriculum.setSelectedClass(e.target.value)}
              options={curriculum.classes.map((c) => ({
                value: c,
                label: `Class ${c}`,
              }))}
              disabled={source === "document"}
            />
            <Select
              label="Subject"
              value={curriculum.selectedSubject}
              onChange={(e) => curriculum.setSelectedSubject(e.target.value)}
              options={curriculum.subjects.map((s) => ({ value: s, label: s }))}
              disabled={source === "document"}
            />
            <Select
              label="Chapter"
              value={curriculum.selectedChapter}
              onChange={(e) => curriculum.setSelectedChapter(e.target.value)}
              options={curriculum.chapters.map((ch) => ({
                value: ch.chapter_title,
                label: ch.chapter_title,
              }))}
              disabled={source === "document"}
            />
            <Select
              label="Document"
              value={selectedDocument || documents[0]?.id || ""}
              onChange={(e) => setSelectedDocument(e.target.value)}
              options={documents.map((doc) => ({
                value: doc.id,
                label: doc.filename,
              }))}
              placeholder="No documents"
              disabled={source === "saksham" || documents.length === 0}
            />
          </div>
        </Card>
<div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
        
          {quizModes.map((mode, i) => {
            const Icon = mode.icon;
            const isActive = activeMode === mode.title;
            return (
              <motion.div
                key={mode.title}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
              >
                <Card
                  hover
                  className={`cursor-pointer h-full ${isActive ? "ring-2 ring-accent" : ""}`}
                  onClick={() => !quizLoading && handleGenerate(mode)}
                >
                  <div className="w-12 h-12 rounded-2xl bg-primary text-white flex items-center justify-center">
                    <Icon size={22} />
                  </div>
                  <h3 className="mt-5 text-lg font-bold text-primary">
                    {mode.title}
                  </h3>
                  <p className="mt-2 text-sm text-ink-muted leading-relaxed">
                    {mode.description}
                  </p>
                  <div className="mt-4 flex items-center gap-1.5 text-sm font-semibold text-accent">
                    {quizLoading && isActive ? "Generating..." : "Start"}
                    <ChevronRight size={16} />
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {quiz.length > 0 && (
          <div className="mt-12">
            <div className="flex items-center gap-3 mb-6">
              <Badge variant="accent">
                <Sparkles size={12} />
                {activeMode}
              </Badge>
              <span className="text-sm text-ink-muted">
                {quiz.length} questions
              </span>
            </div>
            <QuizPanel
              quiz={quiz}
              selectedAnswers={selectedAnswers}
              setSelectedAnswers={setSelectedAnswers}
              quizSubmitted={quizSubmitted}
              onSubmit={submitQuiz}
              score={score}
              topic={curriculum.selectedChapter}
              subject={curriculum.selectedSubject}
              classLevel={curriculum.selectedClass}
            />
          </div>
        )}

        {quizAttempts.length > 0 && (
          <Card className="mt-12">
            <h3 className="font-bold text-primary">Recent Attempts</h3>
            <div className="mt-4 space-y-3">
              {quizAttempts.slice(0, 5).map((attempt) => (
                <div
                  key={attempt.id}
                  className="flex items-center justify-between py-3 border-b border-border last:border-0"
                >
                  <div>
                    <p className="text-sm font-medium text-ink">
                      {attempt.subject} · {attempt.chapter}
                    </p>
                    <p className="text-xs text-ink-muted mt-0.5">
                      Class {attempt.classLevel}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-primary">{attempt.percentage}%</p>
                    <p className="text-xs text-ink-muted">
                      {attempt.score}/{attempt.total}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        )}

        {documents.length === 0 && (
          <Card className="mt-10 text-center py-10">
            <p className="text-ink-muted">
              Curriculum quizzes work immediately. Upload study material if you
              also want quizzes from your own notes.
            </p>
            <Button to="/upload" icon={ChevronRight} className="mt-4">
              Upload Notes
            </Button>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}
