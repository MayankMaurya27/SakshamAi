import { motion } from "framer-motion";
import {
  FileText,
  BookOpen,
  Trophy,
  Clock,
  TrendingUp,
  ArrowRight,
  Flame,
  Star,
  Zap,
  Target,
  Award,
  AlertTriangle,
  BarChart3,
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

function XPBar({ totalXP, getLevel, getNextLevel, getLevelProgress }) {
  const level = getLevel();
  const next = getNextLevel();
  const progress = getLevelProgress();

  return (
    <Card className="bg-gradient-to-r from-primary/8 to-accent/8 border-primary/20">
      <div className="flex items-center gap-4">
        <div className="w-14 h-14 rounded-2xl bg-primary/15 flex items-center justify-center border border-primary/30">
          <span className="text-2xl font-black text-primary">{level.level}</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-bold text-primary">{level.title}</p>
              <span className="text-xs px-2 py-0.5 rounded-full bg-gold/15 text-gold font-bold border border-gold/25">
                {totalXP} XP
              </span>
            </div>
            {next && (
              <p className="text-xs text-ink-muted">
                {next.xpRequired - totalXP} XP to {next.title}
              </p>
            )}
          </div>
          <div className="w-full h-2.5 rounded-full bg-surface overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
        </div>
      </div>
    </Card>
  );
}

function StreakCard({ currentStreak, longestStreak }) {
  const isOnFire = currentStreak >= 3;
  return (
    <Card>
      <div className="flex items-center gap-4">
        <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${
          isOnFire ? "bg-error/15 text-error" : "bg-gold/10 text-gold"
        }`}>
          <Flame size={22} />
        </div>
        <div>
          <p className="text-xs font-semibold text-ink-muted uppercase tracking-wider">
            Learning Streak
          </p>
          <p className="text-2xl font-bold text-primary mt-0.5">
            {currentStreak} {currentStreak === 1 ? "day" : "days"}
          </p>
          <p className="text-xs text-ink-muted">Best: {longestStreak} days</p>
        </div>
      </div>
    </Card>
  );
}

function BadgesGallery({ getUnlockedBadges, getAllBadges }) {
  const unlocked = getUnlockedBadges();
  const all = getAllBadges();
  const unlockedIds = new Set(unlocked.map((b) => b.id));

  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-primary flex items-center gap-2">
          <Award size={20} className="text-gold" />
          Achievements
        </h2>
        <Badge variant="gold">{unlocked.length}/{all.length}</Badge>
      </div>
      <div className="grid grid-cols-5 gap-3">
        {all.map((badge) => {
          const isUnlocked = unlockedIds.has(badge.id);
          return (
            <div
              key={badge.id}
              className={`flex flex-col items-center gap-1 p-2 rounded-xl text-center transition-all ${
                isUnlocked
                  ? "bg-gold/8 border border-gold/20"
                  : "bg-surface/40 border border-border opacity-40 grayscale"
              }`}
              title={`${badge.name}: ${badge.description}`}
            >
              <span className="text-2xl">{badge.icon}</span>
              <span className="text-[10px] font-semibold text-ink-muted leading-tight">
                {badge.name}
              </span>
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function TopicMasteryCard({ getTopicMastery }) {
  const topics = getTopicMastery();
  if (topics.length === 0) {
    return (
      <Card>
        <h2 className="text-lg font-bold text-primary flex items-center gap-2">
          <BarChart3 size={20} className="text-accent" />
          Topic Mastery
        </h2>
        <p className="mt-4 text-sm text-ink-muted text-center py-4">
          Take quizzes to see topic mastery here.
        </p>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="text-lg font-bold text-primary flex items-center gap-2 mb-4">
        <BarChart3 size={20} className="text-accent" />
        Topic Mastery
      </h2>
      <div className="space-y-3">
        {topics.slice(0, 6).map((topic) => (
          <div key={topic.topic}>
            <div className="flex items-center justify-between text-sm mb-1">
              <span className="font-medium text-ink truncate mr-2">{topic.topic}</span>
              <span className={`font-bold ${
                topic.percentage >= 70 ? "text-success" : topic.percentage >= 40 ? "text-gold" : "text-error"
              }`}>
                {topic.percentage}%
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-surface overflow-hidden">
              <motion.div
                className={`h-full rounded-full ${
                  topic.percentage >= 70 ? "bg-success" : topic.percentage >= 40 ? "bg-gold" : "bg-error"
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${topic.percentage}%` }}
                transition={{ duration: 0.6, ease: "easeOut" }}
              />
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}

function ExamReadinessCard({ getExamReadiness, getWeakTopics }) {
  const readiness = getExamReadiness();
  const weakTopics = getWeakTopics();
  const isReady = readiness >= 70;

  return (
    <Card>
      <h2 className="text-lg font-bold text-primary flex items-center gap-2 mb-4">
        <Target size={20} className="text-neural" />
        Exam Readiness
      </h2>
      <div className="flex items-center gap-6">
        <div className="relative w-20 h-20">
          <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              stroke="currentColor"
              strokeWidth="3"
              className="text-surface"
            />
            <motion.path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none"
              strokeWidth="3"
              strokeDasharray={`${readiness}, 100`}
              strokeLinecap="round"
              className={isReady ? "text-success" : "text-gold"}
              initial={{ strokeDasharray: "0, 100" }}
              animate={{ strokeDasharray: `${readiness}, 100` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={`text-xl font-black ${isReady ? "text-success" : "text-gold"}`}>
              {readiness}%
            </span>
          </div>
        </div>
        <div className="flex-1">
          <p className={`text-sm font-semibold ${isReady ? "text-success" : "text-gold"}`}>
            {isReady ? "Ready for exam!" : "Keep practicing!"}
          </p>
          {weakTopics.length > 0 && (
            <div className="mt-2">
              <p className="text-xs text-ink-muted flex items-center gap-1 mb-1">
                <AlertTriangle size={12} className="text-error" />
                Focus areas:
              </p>
              <div className="flex flex-wrap gap-1">
                {weakTopics.slice(0, 3).map((t) => (
                  <span key={t.topic} className="text-xs px-2 py-0.5 rounded-full bg-error/10 text-error border border-error/20 font-medium">
                    {t.topic} ({t.percentage}%)
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

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
    totalXP,
    currentStreak,
    longestStreak,
    getLevel,
    getNextLevel,
    getLevelProgress,
    getUnlockedBadges,
    getAllBadges,
    getTopicMastery,
    getExamReadiness,
    getWeakTopics,
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
          description="Track progress, earn XP, unlock achievements, and follow your personalized learning roadmap."
        />

        {/* XP & Level Bar */}
        <div className="mt-8">
          <XPBar
            totalXP={totalXP}
            getLevel={getLevel}
            getNextLevel={getNextLevel}
            getLevelProgress={getLevelProgress}
          />
        </div>

        {/* Stats Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
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

        {/* Streak + Badges Row */}
        <div className="grid lg:grid-cols-3 gap-6 mt-6">
          <StreakCard currentStreak={currentStreak} longestStreak={longestStreak} />
          <div className="lg:col-span-2">
            <BadgesGallery getUnlockedBadges={getUnlockedBadges} getAllBadges={getAllBadges} />
          </div>
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

        {/* Topic Mastery + Exam Readiness */}
        <div className="grid lg:grid-cols-2 gap-6 mt-6">
          <TopicMasteryCard getTopicMastery={getTopicMastery} />
          <ExamReadinessCard getExamReadiness={getExamReadiness} getWeakTopics={getWeakTopics} />
        </div>

        {/* Concept Map + Learning Roadmap */}
        <div className="grid lg:grid-cols-2 gap-6 mt-6">
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

        {/* Activity Summary + Recent Quizzes */}
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
              <div className="flex items-center justify-between py-3 border-b border-border">
                <span className="text-sm text-ink-muted flex items-center gap-2">
                  <Zap size={14} className="text-gold" />
                  Total XP
                </span>
                <span className="font-bold text-gold">{totalXP}</span>
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
