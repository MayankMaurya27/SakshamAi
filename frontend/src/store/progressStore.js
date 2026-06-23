import { create } from "zustand";
import { persist } from "zustand/middleware";

const useProgressStore = create(
  persist(
    (set, get) => ({
      quizAttempts: [],
      questionsAnswered: 0,
      totalScore: 0,
      bestScore: 0,
      sessionsCount: 0,
      lastActivity: null,

      recordQuizAttempt: ({ score, total, chapter, subject, classLevel }) => {
        const percentage = total > 0 ? Math.round((score / total) * 100) : 0;
        const attempt = {
          id: Date.now(),
          score,
          total,
          percentage,
          chapter,
          subject,
          classLevel,
          timestamp: new Date().toISOString(),
        };

        const state = get();
        const newQuestionsAnswered = state.questionsAnswered + total;
        const newTotalScore = state.totalScore + score;

        set({
          quizAttempts: [attempt, ...state.quizAttempts].slice(0, 50),
          questionsAnswered: newQuestionsAnswered,
          totalScore: newTotalScore,
          bestScore: Math.max(state.bestScore, percentage),
          sessionsCount: state.sessionsCount + 1,
          lastActivity: attempt.timestamp,
        });

        return attempt;
      },

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
