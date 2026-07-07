import { useState, useCallback } from "react";
import { Link } from "react-router-dom";
import {
  FileText,
  Sparkles,
  Copy,
  RefreshCw,
  BookOpen,
  AlertCircle,
} from "lucide-react";

import MainLayout from "../../components/layout/MainLayout";
import PageHeader from "../../components/ui/PageHeader";
import Card from "../../components/ui/Card";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import { LoadingState } from "../../components/ui/Spinner";
import AudioPlayer from "../../components/audio/AudioPlayer";
import KnowledgeBackground from "../../components/background/KnowledgeBackground";

import { useDocuments, useCurriculum } from "../../hooks/useLearning";
import { useSpeechPlayer } from "../../hooks/useSpeechPlayer";

import {
  generateSummary,
  buildLearningPayload,
} from "../../services/learningApi";

const SOURCES = [
  { value: "saksham", label: "Saksham Curriculum" },
  { value: "document", label: "Uploaded Document" },
];

const PROFILES = [
  { value: "standard", label: "Standard Summary" },
  { value: "beginner", label: "Beginner (Simplified)" },
  { value: "dyslexia", label: "Dyslexic (Bullet blocks)" },
];

export default function Summary() {
  const { documents, loading: docsLoading, error: docsError } =
    useDocuments();

  const curriculum = useCurriculum();
  const speech = useSpeechPlayer();

  const [source, setSource] = useState("saksham");
  const [selectedDocument, setSelectedDocument] = useState("");
  const [profile, setProfile] = useState("standard");

  const [summary, setSummary] = useState("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [error, setError] = useState("");

  const activeDocument =
    selectedDocument || (documents[0] ? String(documents[0].id) : "");

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
      source,
      activeDocument,
      curriculum.selectedClass,
      curriculum.selectedSubject,
      curriculum.selectedChapter,
      profile,
    ],
  );

  const handleGenerateSummary = async (regenerate = false) => {
    try {
      setSummaryLoading(true);
      setError("");

      const payload = {
        ...getPayload(),
        regenerate: regenerate === true,
      };

      const result = await generateSummary(payload);

      setSummary(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setSummaryLoading(false);
    }
  };

  const copySummary = async () => {
    if (!summary) return;

    try {
      await navigator.clipboard.writeText(summary);
    } catch (err) {
      console.error(err);
    }
  };

  if (docsLoading || curriculum.loading) {
    return (
      <MainLayout>
        <LoadingState message="Loading Revision Center..." />
      </MainLayout>
    );
  }

  const selectedDoc = documents.find(
    (d) => d.id === Number(activeDocument),
  );

  return (
    <MainLayout>
      <KnowledgeBackground intensity="subtle" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <div className="space-y-4">
          <Badge variant="gold">
            <BookOpen size={12} />
            Revision Workspace
          </Badge>

          <PageHeader
            eyebrow="Saksham Summary"
            title="Revision Center"
            description="Generate concise chapter and document summaries for faster revision and exam preparation."
          />
        </div>

        {(error || docsError || curriculum.error) && (
          <div className="mt-6 flex items-center gap-2 text-sm text-error bg-error/10 border border-error/20 rounded-xl px-4 py-3">
            <AlertCircle size={16} className="shrink-0" />
            {error || docsError || curriculum.error}
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-5 mt-10">
          <Card
            hover
            onClick={() => setSource("saksham")}
            className={`h-full cursor-pointer transition-all duration-300 ${
              source === "saksham"
                ? "!border-accent !bg-accent/10 shadow-glow scale-[1.01]"
                : "border-border hover:!border-accent/30"
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${
                source === "saksham" ? "bg-accent/20" : "bg-primary/10"
              }`}>
                <BookOpen className={source === "saksham" ? "text-accent" : "text-primary"} size={22} />
              </div>

              <div>
                <h3 className="font-bold text-primary">
                  Chapter Summary
                </h3>

                <p className="text-sm text-ink-muted">
                  Generate complete chapter revision notes.
                </p>
              </div>
            </div>
          </Card>

          <Card
            hover
            onClick={() => setSource("document")}
            className={`h-full cursor-pointer transition-all duration-300 ${
              source === "document"
                ? "!border-accent !bg-accent/10 shadow-glow scale-[1.01]"
                : "border-border hover:!border-accent/30"
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center transition-colors duration-300 ${
                source === "document" ? "bg-accent/20" : "bg-primary/10"
              }`}>
                <FileText className={source === "document" ? "text-accent" : "text-primary"} size={22} />
              </div>

              <div>
                <h3 className="font-bold text-primary">
                  Document Summary
                </h3>

                <p className="text-sm text-ink-muted">
                  Generate summaries from uploaded notes and PDFs.
                </p>
              </div>
            </div>
          </Card>
        </div>

        <Card className="mt-8">
          <div className="grid sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <Select
              label="Summary Source"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              options={SOURCES}
            />

            <Select
              label="Class"
              value={curriculum.selectedClass}
              onChange={(e) =>
                curriculum.setSelectedClass(e.target.value)
              }
              options={curriculum.classes.map((c) => ({
                value: c,
                label: `Class ${c}`,
              }))}
              disabled={source === "document"}
            />

            <Select
              label="Subject"
              value={curriculum.selectedSubject}
              onChange={(e) =>
                curriculum.setSelectedSubject(e.target.value)
              }
              options={curriculum.subjects.map((s) => ({
                value: s,
                label: s,
              }))}
              disabled={source === "document"}
            />

            <Select
              label="Chapter"
              value={curriculum.selectedChapter}
              onChange={(e) =>
                curriculum.setSelectedChapter(e.target.value)
              }
              options={curriculum.chapters.map((ch) => ({
                value: ch.chapter_title,
                label: ch.chapter_title,
              }))}
              disabled={source === "document"}
            />

            <Select
              label="Document"
              value={activeDocument}
              onChange={(e) =>
                setSelectedDocument(e.target.value)
              }
              options={documents.map((doc) => ({
                value: doc.id,
                label: doc.filename,
              }))}
              placeholder="No documents"
              disabled={
                source === "saksham" ||
                documents.length === 0
              }
            />

            <Select
              label="Summary Mode"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              options={PROFILES}
            />
          </div>

          <div className="mt-6">
            <Button
              icon={Sparkles}
              loading={summaryLoading}
              onClick={handleGenerateSummary}
              disabled={
                source === "document"
                  ? !activeDocument
                  : !curriculum.selectedChapter
              }
            >
              {summaryLoading
                ? "Generating..."
                : "Generate Summary"}
            </Button>
          </div>

          {source === "document" && documents.length === 0 && (
            <div className="mt-6 flex items-center gap-2 text-sm text-primary bg-primary/10 border border-primary/20 rounded-xl px-4 py-3">
              <AlertCircle size={16} className="shrink-0 text-primary" />
              <span>
                No documents found. Please upload a PDF document in the{" "}
                <Link to="/upload" className="underline font-medium hover:text-primary-light">
                  Upload section
                </Link>{" "}
                first.
              </span>
            </div>
          )}
        </Card>

        {summary && (
          <Card className="mt-8">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
              <div>
                <h2 className="text-xl font-bold text-primary">
                  Generated Summary
                </h2>

                <p className="text-sm text-ink-muted mt-1">
                  {source === "document"
                    ? selectedDoc?.filename
                    : `Class ${curriculum.selectedClass} • ${curriculum.selectedSubject} • ${curriculum.selectedChapter}`}
                </p>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  icon={Copy}
                  onClick={copySummary}
                >
                  Copy
                </Button>

                <Button
                  variant="secondary"
                  icon={RefreshCw}
                  onClick={() => handleGenerateSummary(true)}
                >
                  Regenerate
                </Button>
              </div>
            </div>

            <div className="prose-content whitespace-pre-wrap leading-relaxed text-[15px]">
              {summary}
            </div>

            <div className="mt-6 pt-6 border-t border-border">
              <AudioPlayer
                text={summary}
                status={speech.status}
                volume={speech.volume}
                rate={speech.rate}
                onToggle={speech.toggle}
                onStop={speech.stop}
                onVolumeChange={speech.setVolume}
                onRateChange={speech.setRate}
                label="Narrate Summary"
              />
            </div>
          </Card>
        )}
      </div>
    </MainLayout>
  );
}