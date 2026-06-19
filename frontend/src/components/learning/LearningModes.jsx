import { useState } from "react";
import { motion } from "framer-motion";

const modes = [
  {
    title: "Understand",
    description:
      "Receive clear explanations tailored to your learning level.",
  },
  {
    title: "Practice",
    description:
      "Generate exercises and reinforce your knowledge.",
  },
  {
    title: "Revise",
    description:
      "Create summaries and revision materials instantly.",
  },
  {
    title: "Quiz",
    description:
      "Test understanding with intelligent assessments.",
  },
];

export default function LearningModes() {
  const [active, setActive] = useState(0);

  return (
    <section className="py-28">

      <div className="max-w-7xl mx-auto px-6">

        <div className="text-center">

          <p className="text-sm uppercase tracking-widest text-slate-500">
            Learning Modes
          </p>

          <h2 className="mt-4 text-5xl font-bold text-[#1E3A5F]">
            Learn Your Way
          </h2>

        </div>

        <div className="mt-16 flex gap-4 h-[320px]">

          {modes.map((mode, index) => (
            <motion.div
              key={mode.title}
              onMouseEnter={() => setActive(index)}
              animate={{
                flex:
                  active === index
                    ? 3
                    : 1,
              }}
              transition={{
                duration: 0.4,
              }}
              className="
                rounded-[32px]
                bg-white
                border
                border-slate-200
                shadow-lg
                cursor-pointer
                overflow-hidden
                p-8
                flex
                flex-col
                justify-end
              "
            >
              <h3 className="text-3xl font-bold text-[#1E3A5F]">
                {mode.title}
              </h3>

              {active === index && (
                <motion.p
                  initial={{
                    opacity: 0,
                    y: 20,
                  }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  className="mt-4 text-slate-600"
                >
                  {mode.description}
                </motion.p>
              )}
            </motion.div>
          ))}

        </div>

      </div>

    </section>
  );
}