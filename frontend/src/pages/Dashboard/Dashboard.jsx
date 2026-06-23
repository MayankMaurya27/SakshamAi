import {
  FileText,
  BookOpen,
  Trophy,
  Clock,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeader from "../../components/ui/PageHeader";
import Card from "../../components/ui/Card";
import Select from "../../components/ui/Select";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import { LoadingState } from "../../components/ui/Spinner";
import ConceptMap from "../../components/dashboard/ConceptMap";
import LearningRoadmap from "../../components/dashboard/LearningRoadmap";
import KnowledgeBackground from "../../components/background/KnowledgeBackground";
import { useDocuments, useCurriculum } from "../../hooks/useLearning";
import useProgressStore from "../../store/progressStore";

export default function Dashboard() {
  const { documents, loading: docsLoading } = useDocuments();
  const curriculum = useCurriculum();
  const {
    questionsAnswered,
    getAverageScore,
    bestScore,
    sessionsCount,
    quizAttempts,
    lastActivity,
  } = useProgressStore();

  if (docsLoading || curriculum.loading) {
    return (
      <MainLayout>
        <LoadingState message="Loading dashboard..." />
      </MainLayout>
    );
  }

  const stats = [
    {
      icon: FileText,
      label: "Documents",
      value: documents.length,
      color: "primary",
    },
    {
      icon: BookOpen,
      label: "Chapters",
      value: curriculum.chapters.length,
      color: "accent",
    },
    {
      icon: Trophy,
      label: "Best Score",
      value: `${bestScore}%`,
      color: "gold",
    },
    {
      icon: TrendingUp,
      label: "Avg Score",
      value: `${getAverageScore()}%`,
      color: "neural",
    },
  ];

  const colorMap = {
    primary: "bg-primary/10 text-primary",
    accent: "bg-accent/10 text-accent",
    gold: "bg-gold/10 text-gold",
    neural: "bg-neural/10 text-neural",
  };

  return (
    <MainLayout>
      <KnowledgeBackground intensity="subtle" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <PageHeader
          eyebrow="Learning Intelligence"
          title="Your Dashboard"
          description="Track progress, explore concept maps, and follow your personalized learning roadmap."
        />

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.label}>
                <div className="flex items-center gap-4">
                  <div
                    className={`w-11 h-11 rounded-xl flex items-center justify-center ${colorMap[stat.color]}`}
                  >
                    <Icon size={20} />
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-ink-muted uppercase tracking-wider">
                      {stat.label}
                    </p>
                    <p className="text-2xl font-bold text-primary mt-0.5">
                      {stat.value}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        <Card className="mt-6">
          <div className="grid sm:grid-cols-3 gap-4">
            <Select
              label="Class"
              value={curriculum.selectedClass}
              onChange={(e) => curriculum.setSelectedClass(e.target.value)}
              options={curriculum.classes.map((c) => ({
                value: c,
                label: `Class ${c}`,
              }))}
            />
            <Select
              label="Subject"
              value={curriculum.selectedSubject}
              onChange={(e) => curriculum.setSelectedSubject(e.target.value)}
              options={curriculum.subjects.map((s) => ({ value: s, label: s }))}
            />
            <Select
              label="Current Chapter"
              value={curriculum.selectedChapter}
              onChange={(e) => curriculum.setSelectedChapter(e.target.value)}
              options={curriculum.chapters.map((ch) => ({
                value: ch.chapter_title,
                label: ch.chapter_title,
              }))}
            />
          </div>
        </Card>

        <div className="grid lg:grid-cols-2 gap-6 mt-8">
          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-primary">Concept Map</h2>
              <Badge variant="neural">Knowledge Graph</Badge>
            </div>
            <ConceptMap
              chapters={curriculum.chapters}
              subject={curriculum.selectedSubject}
              classLevel={curriculum.selectedClass}
            />
          </Card>

          <Card>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-primary">Learning Roadmap</h2>
              <Badge variant="accent">Progress Path</Badge>
            </div>
            <LearningRoadmap
              chapters={curriculum.chapters}
              selectedChapter={curriculum.selectedChapter}
            />
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mt-6">
          <Card>
            <h2 className="text-lg font-bold text-primary">Activity Summary</h2>
            <div className="mt-5 space-y-4">
              <div className="flex items-center justify-between py-3 border-b border-border">
                <span className="text-sm text-ink-muted">Quiz Sessions</span>
                <span className="font-bold text-primary">{sessionsCount}</span>
              </div>
              <div className="flex items-center justify-between py-3 border-b border-border">
                <span className="text-sm text-ink-muted">Questions Attempted</span>
                <span className="font-bold text-primary">{questionsAnswered}</span>
              </div>
              <div className="flex items-center justify-between py-3">
                <span className="text-sm text-ink-muted flex items-center gap-2">
                  <Clock size={14} />
                  Last Activity
                </span>
                <span className="text-sm font-medium text-ink">
                  {lastActivity
                    ? new Date(lastActivity).toLocaleDateString()
                    : "No activity yet"}
                </span>
              </div>
            </div>
          </Card>

          <Card>
            <h2 className="text-lg font-bold text-primary">Recent Quizzes</h2>
            {quizAttempts.length === 0 ? (
              <div className="mt-6 text-center py-8">
                <p className="text-ink-muted text-sm">No quiz attempts yet.</p>
                <Button to="/quiz" size="sm" icon={ArrowRight}>
                  Take a Quiz
                </Button>
              </div>
            ) : (
              <div className="mt-4 space-y-3">
                {quizAttempts.slice(0, 4).map((attempt) => (
                  <div
                    key={attempt.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-surface"
                  >
                    <div>
                      <p className="text-sm font-medium text-ink">
                        {attempt.chapter}
                      </p>
                      <p className="text-xs text-ink-muted">
                        {attempt.subject} · Class {attempt.classLevel}
                      </p>
                    </div>
                    <span
                      className={`text-sm font-bold ${
                        attempt.percentage >= 70
                          ? "text-success"
                          : attempt.percentage >= 40
                            ? "text-gold"
                            : "text-error"
                      }`}
                    >
                      {attempt.percentage}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        <Card className="mt-6 bg-gradient-to-r from-primary/8 to-accent/8 border-primary/15">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <h3 className="font-bold text-primary">Continue Learning</h3>
              <p className="text-sm text-ink-muted mt-1">
                Pick up where you left off in the learning workspace.
              </p>
            </div>
            <Button to="/learn" icon={ArrowRight}>
              Go to Workspace
            </Button>
          </div>
        </Card>
      </div>
    </MainLayout>
  );
}
