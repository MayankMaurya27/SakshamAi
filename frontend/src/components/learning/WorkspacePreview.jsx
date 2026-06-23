import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Brain,
  BookOpen,
  Accessibility,
  FileText,
} from "lucide-react";

const tabs = [
  {
    id: "learn",
    icon: BookOpen,
    title: "Learn",
    heading: "AI-Powered Learning",
    description:
      "Ask questions from uploaded notes and receive curriculum-aware explanations adapted to the student's level.",
  },
  {
    id: "quiz",
    icon: Brain,
    title: "Quiz",
    heading: "Smart Assessment",
    description:
      "Generate quizzes instantly and evaluate understanding through interactive practice.",
  },
  {
    id: "accessibility",
    icon: Accessibility,
    title: "Accessibility",
    heading: "Learning For Everyone",
    description:
      "Support beginner learners, dyslexic learners and visually impaired students with adaptive content.",
  },
  {
    id: "revision",
    icon: FileText,
    title: "Revision",
    heading: "Quick Revision",
    description:
      "Generate summaries, notes and revision material for faster learning.",
  },
];

export default function WorkspacePreview() {
  const [active, setActive] = useState(tabs[0]);

  return (
    <section
      id="workspace-preview"
      className="py-20"
    >
      <div className="max-w-7xl mx-auto px-6">

        <div className="text-center">

          <p className="uppercase tracking-[0.35em] text-sm text-slate-500">
            Learning Workspace
          </p>

          <h2 className="mt-4 text-4xl md:text-6xl font-bold text-[#1E3A5F]">
            Explore The Platform
          </h2>

          <p className="mt-6 max-w-3xl mx-auto text-slate-600">
            A unified learning environment designed for
            understanding, practice, revision and accessibility.
          </p>

        </div>

        {/* Tabs */}

        <div className="flex flex-wrap justify-center gap-4 mt-14">

          {tabs.map((tab) => {
            const Icon = tab.icon;

            return (
              <button
                key={tab.id}
                onClick={() => setActive(tab)}
                className={`
                  flex
                  items-center
                  gap-3
                  px-5
                  py-3
                  rounded-full
                  transition-all
                  border
                  ${
                    active.id === tab.id
                      ? "bg-[#1E3A5F] text-white border-[#1E3A5F]"
                      : "bg-white/70 text-slate-700 border-slate-200"
                  }
                `}
              >
                <Icon size={18} />
                {tab.title}
              </button>
            );
          })}

        </div>

        {/* Showcase */}

        <AnimatePresence mode="wait">

          <motion.div
            key={active.id}
            initial={{
              opacity: 0,
              y: 20,
            }}
            animate={{
              opacity: 1,
              y: 0,
            }}
            exit={{
              opacity: 0,
              y: -20,
            }}
            transition={{
              duration: 0.35,
            }}
            className="
              mt-12
              bg-white/80
              backdrop-blur-md
              border
              border-slate-200
              rounded-[40px]
              overflow-hidden
              shadow-xl
            "
          >

            <div className="grid lg:grid-cols-2">

              {/* Left */}

              <div className="p-10">

                <div className="text-sm uppercase tracking-widest text-slate-500">
                  {active.title}
                </div>

                <h3
                  className="
                    mt-4
                    text-4xl
                    font-bold
                    text-[#1E3A5F]
                  "
                >
                  {active.heading}
                </h3>

                <p
                  className="
                    mt-6
                    text-lg
                    leading-relaxed
                    text-slate-600
                  "
                >
                  {active.description}
                </p>

                <div className="mt-10 space-y-4">

                  <div className="flex gap-3">
                    <div className="w-2 h-2 rounded-full bg-[#1E3A5F] mt-2" />
                    Curriculum Aware
                  </div>

                  <div className="flex gap-3">
                    <div className="w-2 h-2 rounded-full bg-[#1E3A5F] mt-2" />
                    Personalized Learning
                  </div>

                  <div className="flex gap-3">
                    <div className="w-2 h-2 rounded-full bg-[#1E3A5F] mt-2" />
                    Offline Ready
                  </div>

                </div>

              </div>

              {/* Right */}

              <div
                className="
                  bg-gradient-to-br
                  from-slate-50
                  to-slate-100
                  min-h-[420px]
                  flex
                  items-center
                  justify-center
                  p-10
                "
              >

                {/* Replace this later with real screenshots */}

                <div
                  className="
                    w-full
                    h-[320px]
                    rounded-[28px]
                    border-2
                    border-dashed
                    border-slate-300
                    flex
                    items-center
                    justify-center
                    text-slate-400
                    text-center
                    text-lg
                    font-medium
                  "
                >
                  {active.title} Screenshot
                  <br />
                  (Replace Later)
                </div>

              </div>

            </div>

          </motion.div>

        </AnimatePresence>

      </div>
    </section>
  );
}