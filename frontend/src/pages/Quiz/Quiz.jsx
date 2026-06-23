import MainLayout from "../../components/layout/MainLayout";
import {
  Brain,
  BookOpen,
  Trophy,
  Target,
  ChevronRight,
} from "lucide-react";

export default function Quiz() {
  const quizModes = [
    {
      icon: BookOpen,
      title: "Curriculum Quiz",
      description: "Generate quizzes from your syllabus and chapters.",
    },
    {
      icon: Brain,
      title: "Revision Quiz",
      description: "Quick revision before tests and examinations.",
    },
    {
      icon: Target,
      title: "Chapter Challenge",
      description: "Focus on a specific topic or chapter.",
    },
    {
      icon: Trophy,
      title: "Challenge Mode",
      description: "Mixed questions with increasing difficulty.",
    },
  ];

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto px-6 py-12">

        {/* Header */}

        <div className="text-center">

          <p className="uppercase tracking-[0.3em] text-sm text-slate-500">
            Assessment Workspace
          </p>

          <h1 className="mt-4 text-5xl md:text-6xl font-bold text-[#1E3A5F]">
            Quiz Center
          </h1>

          <p className="mt-6 max-w-2xl mx-auto text-slate-600 text-lg">
            Practice concepts, test understanding and track learning progress.
          </p>

        </div>

        {/* Modes */}

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">

          {quizModes.map((mode) => {
            const Icon = mode.icon;

            return (
              <div
                key={mode.title}
                className="
                  group
                  bg-white/80
                  backdrop-blur-md
                  border
                  border-slate-200
                  rounded-[32px]
                  p-6
                  shadow-lg
                  hover:-translate-y-2
                  transition-all
                  cursor-pointer
                "
              >
                <div
                  className="
                    w-14
                    h-14
                    rounded-2xl
                    bg-[#1E3A5F]
                    text-white
                    flex
                    items-center
                    justify-center
                  "
                >
                  <Icon size={26} />
                </div>

                <h3 className="mt-6 text-xl font-bold text-[#1E3A5F]">
                  {mode.title}
                </h3>

                <p className="mt-3 text-slate-600 text-sm leading-relaxed">
                  {mode.description}
                </p>

                <div className="mt-6 flex items-center gap-2 text-[#1E3A5F] font-medium">
                  Explore
                  <ChevronRight size={18} />
                </div>

              </div>
            );
          })}

        </div>

        {/* Stats */}

        <div className="grid md:grid-cols-3 gap-6 mt-16">

          <div className="bg-white rounded-3xl border border-slate-200 p-8">
            <p className="text-slate-500">Questions Attempted</p>
            <h3 className="mt-3 text-4xl font-bold text-[#1E3A5F]">0</h3>
          </div>

          <div className="bg-white rounded-3xl border border-slate-200 p-8">
            <p className="text-slate-500">Average Score</p>
            <h3 className="mt-3 text-4xl font-bold text-[#1E3A5F]">0%</h3>
          </div>

          <div className="bg-white rounded-3xl border border-slate-200 p-8">
            <p className="text-slate-500">Best Score</p>
            <h3 className="mt-3 text-4xl font-bold text-[#1E3A5F]">0%</h3>
          </div>

        </div>

        {/* CTA */}

        <div
          className="
            mt-16
            bg-white/80
            backdrop-blur-md
            border
            border-slate-200
            rounded-[36px]
            p-10
            text-center
          "
        >
          <h2 className="text-3xl font-bold text-[#1E3A5F]">
            Ready To Practice?
          </h2>

          <p className="mt-4 text-slate-600">
            Generate a personalized quiz and strengthen your understanding.
          </p>

          <button
            className="
              mt-8
              px-8
              py-4
              rounded-2xl
              bg-[#1E3A5F]
              text-white
              font-semibold
            "
          >
            Start Quiz
          </button>
        </div>

      </div>
    </MainLayout>
  );
}   