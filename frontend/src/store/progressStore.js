import { create } from "zustand";
import { persist } from "zustand/middleware";

// --- XP & Level Configuration ---
const XP_PER_CORRECT = 15;
const XP_PER_ATTEMPT = 5;
const XP_PERFECT_BONUS = 50;
const XP_STREAK_BONUS = 25;

const LEVELS = [
  { level: 1, xpRequired: 0, title: "Beginner" },
  { level: 2, xpRequired: 100, title: "Explorer" },
  { level: 3, xpRequired: 300, title: "Learner" },
  { level: 4, xpRequired: 600, title: "Scholar" },
  { level: 5, xpRequired: 1000, title: "Expert" },
  { level: 6, xpRequired: 1500, title: "Master" },
  { level: 7, xpRequired: 2200, title: "Guru" },
  { level: 8, xpRequired: 3000, title: "Legend" },
];

function getLevelForXP(xp) {
  let current = LEVELS[0];
  for (const lvl of LEVELS) {
    if (xp >= lvl.xpRequired) current = lvl;
    else break;
  }
  return current;
}

function getNextLevel(xp) {
  for (const lvl of LEVELS) {
    if (xp < lvl.xpRequired) return lvl;
  }
  return null;
}

// --- Achievement Definitions ---
const BADGE_DEFINITIONS = [
  { id: "first_quiz", name: "First Steps", icon: "🎯", description: "Complete your first quiz", check: (s) => s.sessionsCount >= 1 },
  { id: "ten_quizzes", name: "Quiz Pro", icon: "📝", description: "Complete 10 quizzes", check: (s) => s.sessionsCount >= 10 },
  { id: "fifty_questions", name: "Knowledge Seeker", icon: "🔍", description: "Answer 50 questions", check: (s) => s.questionsAnswered >= 50 },
  { id: "hundred_questions", name: "Century Club", icon: "💯", description: "Answer 100 questions", check: (s) => s.questionsAnswered >= 100 },
  { id: "perfect_score", name: "Perfectionist", icon: "⭐", description: "Get a perfect quiz score", check: (s) => s.bestScore >= 100 },
  { id: "high_scorer", name: "High Achiever", icon: "🏆", description: "Score 80% or above", check: (s) => s.bestScore >= 80 },
  { id: "streak_3", name: "On Fire", icon: "🔥", description: "Maintain a 3-day streak", check: (s) => s.currentStreak >= 3 },
  { id: "streak_7", name: "Unstoppable", icon: "💪", description: "Maintain a 7-day streak", check: (s) => s.currentStreak >= 7 },
  { id: "level_5", name: "Expert Level", icon: "🎓", description: "Reach Level 5", check: (s) => getLevelForXP(s.totalXP).level >= 5 },
  { id: "multi_subject", name: "Renaissance", icon: "🌟", description: "Quiz in 3+ subjects", check: (s) => Object.keys(s.topicScores).length >= 3 },
];

function getDateKey(isoString) {
  if (!isoString) return null;
  return isoString.split("T")[0];
}

function isConsecutiveDay(prev, current) {
  if (!prev) return false;
  const d1 = new Date(prev);
  const d2 = new Date(current);
  d1.setHours(0, 0, 0, 0);
  d2.setHours(0, 0, 0, 0);
  const diff = (d2 - d1) / (1000 * 60 * 60 * 24);
  return diff === 1;
}

function isSameDay(prev, current) {
  return getDateKey(prev) === getDateKey(current);
}

const useProgressStore = create(
  persist(
    (set, get) => ({
      // --- Core quiz tracking (preserved from original) ---
      quizAttempts: [],
      questionsAnswered: 0,
      totalScore: 0,
      bestScore: 0,
      sessionsCount: 0,
      lastActivity: null,

      // --- New: XP & Gamification ---
      totalXP: 0,
      earnedBadges: [],

      // --- New: Streak tracking ---
      currentStreak: 0,
      longestStreak: 0,
      lastActiveDate: null,

      // --- New: Per-topic mastery tracking ---
      topicScores: {},
      // Structure: { "Mathematics": { attempts: 5, correct: 20, total: 25 }, ... }

      // --- New: Weak topic detection ---
      getWeakTopics: () => {
        const { topicScores } = get();
        const topics = Object.entries(topicScores)
          .map(([topic, data]) => ({
            topic,
            percentage: data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0,
            attempts: data.attempts,
          }))
          .filter((t) => t.attempts >= 1 && t.percentage < 60)
          .sort((a, b) => a.percentage - b.percentage);
        return topics;
      },

      // --- New: Topic mastery map ---
      getTopicMastery: () => {
        const { topicScores } = get();
        return Object.entries(topicScores).map(([topic, data]) => ({
          topic,
          percentage: data.total > 0 ? Math.round((data.correct / data.total) * 100) : 0,
          attempts: data.attempts,
          total: data.total,
          correct: data.correct,
        })).sort((a, b) => b.percentage - a.percentage);
      },

      // --- New: Exam readiness score ---
      getExamReadiness: () => {
        const { topicScores } = get();
        const topics = Object.values(topicScores);
        if (topics.length === 0) return 0;
        const totalCorrect = topics.reduce((sum, t) => sum + t.correct, 0);
        const totalQuestions = topics.reduce((sum, t) => sum + t.total, 0);
        return totalQuestions > 0 ? Math.round((totalCorrect / totalQuestions) * 100) : 0;
      },

      // --- New: Level info ---
      getLevel: () => getLevelForXP(get().totalXP),
      getNextLevel: () => getNextLevel(get().totalXP),
      getLevelProgress: () => {
        const xp = get().totalXP;
        const current = getLevelForXP(xp);
        const next = getNextLevel(xp);
        if (!next) return 100;
        const range = next.xpRequired - current.xpRequired;
        const progress = xp - current.xpRequired;
        return Math.round((progress / range) * 100);
      },

      // --- New: Unlocked badges ---
      getUnlockedBadges: () => {
        const state = get();
        return BADGE_DEFINITIONS.filter((b) => b.check(state));
      },

      getAllBadges: () => BADGE_DEFINITIONS,

      // --- Original method (enhanced) ---
      recordQuizAttempt: ({ score, total, chapter, subject, classLevel }) => {
        const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
        const now = new Date().toISOString();
        const attempt = {
          id: Date.now(),
          score,
          total,
          percentage,
          chapter,
          subject,
          classLevel,
          timestamp: now,
        };

        const state = get();
        const newQuestionsAnswered = state.questionsAnswered + total;
        const newTotalScore = state.totalScore + score;

        // --- XP Calculation ---
        let xpEarned = XP_PER_ATTEMPT;
        xpEarned += score * XP_PER_CORRECT;
        if (percentage === 100) xpEarned += XP_PERFECT_BONUS;

        // --- Streak logic ---
        let newStreak = state.currentStreak;
        const todayKey = getDateKey(now);
        const lastKey = state.lastActiveDate;

        if (!isSameDay(lastKey, todayKey)) {
          if (isConsecutiveDay(lastKey, todayKey)) {
            newStreak += 1;
            xpEarned += XP_STREAK_BONUS;
          } else if (lastKey) {
            newStreak = 1; // streak broken
          } else {
            newStreak = 1; // first ever
          }
        }
        // If same day, don't increment streak

        // --- Per-topic tracking ---
        const topicKey = subject || chapter || "General";
        const topicScores = { ...state.topicScores };
        if (!topicScores[topicKey]) {
          topicScores[topicKey] = { attempts: 0, correct: 0, total: 0 };
        }
        topicScores[topicKey] = {
          attempts: topicScores[topicKey].attempts + 1,
          correct: topicScores[topicKey].correct + score,
          total: topicScores[topicKey].total + total,
        };

        set({
          quizAttempts: [attempt, ...state.quizAttempts].slice(0, 50),
          questionsAnswered: newQuestionsAnswered,
          totalScore: newTotalScore,
          bestScore: Math.max(state.bestScore, percentage),
          sessionsCount: state.sessionsCount + 1,
          lastActivity: now,
          totalXP: state.totalXP + xpEarned,
          currentStreak: newStreak,
          longestStreak: Math.max(state.longestStreak, newStreak),
          lastActiveDate: todayKey,
          topicScores,
        });

        return { ...attempt, xpEarned };
      },

      // --- Original method (preserved) ---
      getAverageScore: () => {
        const { questionsAnswered, totalScore } = get();
        if (questionsAnswered === 0) return 0;
        return Math.round((totalScore / questionsAnswered) * 100);
      },
    }),
    { name: "saksham-progress" },
  ),
);

export default useProgressStore;
