import { useState, useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Send, FileText, BookMarked, AlertCircle } from "lucide-react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeader from "../../components/ui/PageHeader";
import Card from "../../components/ui/Card";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import { LoadingState } from "../../components/ui/Spinner";
import LearningTools from "../../components/learning/LearningTools";
import QuizPanel from "../../components/learning/QuizPanel";
import AudioPlayer from "../../components/audio/AudioPlayer";
import KnowledgeBackground from "../../components/background/KnowledgeBackground";
import StudyCoach from "../../components/learning/StudyCoach";
import { useDocuments, useCurriculum } from "../../hooks/useLearning";
import { useSpeechPlayer } from "../../hooks/useSpeechPlayer";
import {
  askQuestion,
  simplifyExplanation,
  localizeHindi,
  generateQuiz,
  buildLearningPayload,
} from "../../services/learningApi";
import useProgressStore from "../../store/progressStore";

const TABS = [
  { id: "answer", label: "Answer" },
  { id: "simplify", label: "Simplified" },
  { id: "hindi", label: "Hindi" },
  { id: "quiz", label: "Quiz" },
];

const PROFILES = [
  { value: "beginner", label: "Beginner" },
  { value: "dyslexia", label: "Dyslexia Friendly" },
  { value: "visual", label: "Visually Impaired" },
];

const SOURCES = [
  { value: "saksham", label: "Saksham Curriculum" },
  { value: "document", label: "Uploaded Document" },
];

const LOADING_MESSAGES = {
  answer: "Generating answer...",
 
  simplify: "Simplifying...",
  hindi: "Translating...",
};

export default function Learn() {
  const [searchParams] = useSearchParams();
  const profileParam = searchParams.get("profile");
  const sourceParam = searchParams.get("source");
  const documentParam = searchParams.get("document");

  const { documents, loading: docsLoading, error: docsError } = useDocuments();
  const curriculum = useCurriculum();
  const speech = useSpeechPlayer();
  const recordQuizAttempt = useProgressStore((s) => s.recordQuizAttempt);

  const [selectedDocument, setSelectedDocument] = useState(documentParam || "");
  const activeDocument =
    selectedDocument || (documents[0] ? String(documents[0].id) : "");

  const [profile, setProfile] = useState(() =>
    ["beginner", "dyslexia", "visual"].includes(profileParam)
      ? profileParam
      : "beginner",
  );
  const [source, setSource] = useState(
    sourceParam === "document" ? "document" : "saksham",
  );

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [hasResponse, setHasResponse] = useState(false);
  const [error, setError] = useState("");

 
  const [simplifiedText, setSimplifiedText] = useState("");
  const [simplifyLoading, setSimplifyLoading] = useState(false);
  const [hindiText, setHindiText] = useState("");
  const [hindiLoading, setHindiLoading] = useState(false);

  const [quiz, setQuiz] = useState([]);
  const [quizLoading, setQuizLoading] = useState(false);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [score, setScore] = useState(null);
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  const [activeTab, setActiveTab] = useState("answer");

  const getPayload = useCallback(
    () =>
      buildLearningPayload({
        source,
        documentId: activeDocument,
        classLevel: curriculum.selectedClass,
        subject: curriculum.selectedSubject,
        chapter: curriculum.selectedChapter,
        profile,
      }),
    [
      activeDocument,
      source,
      curriculum.selectedClass,
      curriculum.selectedSubject,
      curriculum.selectedChapter,
      profile,
    ],
  );

  const handleAsk = async () => {
    if (!question.trim()) return;
    if (source === "document" && !activeDocument) {
      setError("Please upload or select a document first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      const result = await askQuestion({
        question,
        ...getPayload(),
        topic: "",
        mode: "learn",
      });
      setAnswer(result);
      setHasResponse(true);
      setActiveTab("answer");
      setQuiz([]);
      setQuizSubmitted(false);
      setScore(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  

  const handleSimplify = async () => {
    if (!question.trim() && !answer.trim()) {
      setError("Ask a question first, or generate an answer to simplify.");
      return;
    }
    try {
      setSimplifyLoading(true);
      setError("");
      const result = await simplifyExplanation({
        question: question || answer.slice(0, 200),
        ...getPayload(),
        topic: "",
      });
      setSimplifiedText(result);
      setActiveTab("simplify");
      setHasResponse(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setSimplifyLoading(false);
    }
  };

  const handleHindi = async () => {
    if (!answer.trim()) {
      setError("Generate an answer first, then translate to Hindi.");
      return;
    }
    try {
      setHindiLoading(true);
      setError("");
      const localizationPayload = {
        text: answer,
        content_type: "answer",
        subject: curriculum.selectedSubject,
        include_audio: false,
        preserve_terms: [],
      };
      if (curriculum.selectedClass) {
        localizationPayload.class_level = Number(curriculum.selectedClass);
      }
      const result = await localizeHindi(localizationPayload);
      setHindiText(result);
      setActiveTab("hindi");
      setHasResponse(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setHindiLoading(false);
    }
  };

  const handleQuiz = async () => {
    if (source === "document" && !activeDocument) {
      setError("Please upload or select a document first.");
      return;
    }
    try {
      setQuizLoading(true);
      setError("");
      const questions = await generateQuiz({
        ...getPayload(),
        topic: question || curriculum.selectedChapter,
        question_count: 5,
      });
      setQuiz(questions);
      setActiveTab("quiz");
      setHasResponse(true);
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

  const getActiveContent = () => {
    switch (activeTab) {
      case "simplify":
        return simplifyLoading ? LOADING_MESSAGES.simplify : simplifiedText;
      case "hindi":
        return hindiLoading ? LOADING_MESSAGES.hindi : hindiText;
      default:
        return loading ? LOADING_MESSAGES.answer : answer;
    }
  };

  const getSpeakableText = () => {
    const content = getActiveContent();
    if (!content || Object.values(LOADING_MESSAGES).includes(content)) return "";
    return content;
  };

  const visibleTabs = TABS.filter((tab) => {
    if (tab.id === "answer") return hasResponse || answer;
    
    if (tab.id === "simplify") return simplifiedText;
    if (tab.id === "hindi") return hindiText;
    if (tab.id === "quiz") return quiz.length > 0;
    return false;
  });

  const selectedDoc = documents.find(
    (d) => d.id === Number(activeDocument),
  );

  if (docsLoading || curriculum.loading) {
    return (
      <MainLayout>
        <LoadingState message="Preparing your workspace..." />
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <KnowledgeBackground intensity="subtle" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="space-y-4">
          <Badge variant="gold">
            <BookMarked size={12} />
            Study Workspace
          </Badge>
          <PageHeader
            eyebrow="Saksham Learn"
            title="Ask. Understand. Master."
            description="Your curriculum-aware study companion — ask from uploaded materials, generate summaries, quizzes, and adaptive explanations with built-in narration."
          />
        </div>

        {(error || docsError || curriculum.error) && (
          <div className="mt-6 flex items-center gap-2 text-sm text-error bg-error/10 border border-error/20 rounded-xl px-4 py-3">
            <AlertCircle size={16} className="shrink-0" />
            {error || docsError || curriculum.error}
          </div>
        )}

        <Card className="mt-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Select
              label="Learning Source"
              value={source}
              onChange={(e) => {
                setSource(e.target.value);
                setError("");
              }}
              options={SOURCES}
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
              value={activeDocument}
              onChange={(e) => setSelectedDocument(e.target.value)}
              options={documents.map((doc) => ({
                value: doc.id,
                label: doc.filename,
              }))}
              placeholder="No documents"
              disabled={source === "saksham" || documents.length === 0}
            />
            <Select
              label="Learning Profile"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              options={PROFILES}
            />
          </div>
        </Card>

        <div className="mt-8 grid lg:grid-cols-[1fr_320px] gap-6">
          <div className="space-y-6">
            <Card>
              <Textarea
                label="Your Question"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder={
                  source === "document"
                    ? "Ask anything from your uploaded document..."
                    : "Ask anything from the selected curriculum chapter..."
                }
                rows={5}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleAsk();
                }}
              />
              <div className="mt-4 flex flex-wrap gap-3 items-center">
                <Button
                  onClick={handleAsk}
                  loading={loading}
                  icon={Send}
                  disabled={
                    !question.trim() ||
                    (source === "document"
                      ? !activeDocument
                      : !curriculum.selectedChapter)
                  }
                >
                  {loading ? "Generating..." : "Ask Saksham"}
                </Button>
                <span className="text-xs text-ink-faint hidden sm:inline">
                  Ctrl+Enter to submit
                </span>
              </div>
            </Card>

            <AnimatePresence>
              {hasResponse && (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {activeTab !== "quiz" && (
                    <Card>
                      <div className="flex flex-wrap gap-2 mb-6">
                        {visibleTabs
                          .filter((t) => t.id !== "quiz")
                          .map((tab) => (
                            <button
                              key={tab.id}
                              type="button"
                              onClick={() => setActiveTab(tab.id)}
                              className={`
                                px-4 py-2 rounded-full text-sm font-semibold transition-all focus-ring
                                ${
                                  activeTab === tab.id
                                    ? "bg-primary text-void shadow-amber"
                                    : "bg-surface border border-border text-ink-muted hover:border-accent/50 hover:text-accent"
                                }
                              `}
                            >
                              {tab.label}
                            </button>
                          ))}
                        {quiz.length > 0 && (
                          <button
                            type="button"
                            onClick={() => setActiveTab("quiz")}
                            className={`
                              px-4 py-2 rounded-full text-sm font-semibold transition-all focus-ring
                              ${
                                activeTab === "quiz"
                                  ? "bg-primary text-void shadow-amber"
                                  : "bg-surface border border-border text-ink-muted hover:border-accent/50 hover:text-accent"
                              }
                            `}
                          >
                            Quiz
                          </button>
                        )}
                      </div>

                      <div className="prose-content whitespace-pre-wrap leading-relaxed text-[15px]">
                        {getActiveContent()}
                      </div>

                      {activeTab !== "quiz" && getSpeakableText() && (
                        <div className="mt-6 pt-6 border-t border-border">
                          <AudioPlayer
                            text={getSpeakableText()}
                            status={speech.status}
                            volume={speech.volume}
                            rate={speech.rate}
                            onToggle={speech.toggle}
                            onStop={speech.stop}
                            onVolumeChange={speech.setVolume}
                            onRateChange={speech.setRate}
                            label={`Narrate ${activeTab === "answer" ? "Answer" : activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}`}
                          />
                        </div>
                      )}
                    </Card>
                  )}

                  {activeTab === "quiz" && (
                    <QuizPanel
                      quiz={quiz}
                      selectedAnswers={selectedAnswers}
                      setSelectedAnswers={setSelectedAnswers}
                      quizSubmitted={quizSubmitted}
                      onSubmit={submitQuiz}
                      score={score}
                    />
                  )}

                  <Card className="bg-surface/60">
                    <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                      <FileText size={16} className="text-accent" />
                      Sources
                    </div>
                    <p className="mt-2 text-sm text-ink-muted">
                      Source:{" "}
                      <span className="font-medium text-ink">
                        {source === "document"
                          ? selectedDoc?.filename || "None selected"
                          : `Class ${curriculum.selectedClass} · ${curriculum.selectedSubject} · ${curriculum.selectedChapter}`}
                      </span>
                    </p>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {(source === "document" ? activeDocument : curriculum.selectedChapter) && (
            <div className="space-y-4">
              <LearningTools
                onQuiz={handleQuiz}
                
                onSimplify={handleSimplify}
                onHindi={handleHindi}
                quizLoading={quizLoading}
                
                simplifyLoading={simplifyLoading}
                hindiLoading={hindiLoading}
                hasAnswer={Boolean(answer.trim())}
                hasQuestion={Boolean(question.trim())}
              />
              <StudyCoach
                currentChapter={curriculum.selectedChapter}
                onSimplify={handleSimplify}
                hasQuestion={Boolean(question.trim())}
              />
            </div>
          )}
        </div>
      </div>
    </MainLayout>
  );
}
