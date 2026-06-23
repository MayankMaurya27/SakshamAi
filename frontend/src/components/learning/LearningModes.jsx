import { motion } from "framer-motion";

const steps = [
  {
    number: "01",
    title: "Understand",
    description:
      "Ask questions and receive curriculum-aware explanations tailored to your learning level.",
  },
  {
    number: "02",
    title: "Practice",
    description:
      "Strengthen concepts through AI-generated exercises and guided practice.",
  },
  {
    number: "03",
    title: "Revise",
    description:
      "Create smart summaries, revision notes and quick concept refreshers.",
  },
  {
    number: "04",
    title: "Assess",
    description:
      "Evaluate your understanding using quizzes and instant feedback.",
  },
];

export default function LearningModes() {
  return (
    <section id="learning-modes" className="py-20">

      <div className="max-w-7xl mx-auto px-6">

        {/* Heading */}

        <div className="text-center">

          <p className="text-sm uppercase tracking-[0.35em] text-slate-500">
            Student Journey
          </p>

          <h2 className="mt-4 text-4xl md:text-6xl font-bold text-[#1E3A5F]">
            How Learning Progresses
          </h2>

          <p className="mt-6 max-w-2xl mx-auto text-slate-600">
            Saksham AI supports students through every stage of
            learning — from understanding concepts to mastering them.
          </p>

        </div>

        {/* Desktop Timeline */}

        <div className="hidden lg:block mt-24">

  {steps.map((step, index) => (
    <motion.div
      key={step.title}
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.15 }}
      className={`
        flex
        ${index % 2 === 0 ? "justify-start" : "justify-end"}
        mb-20
      `}
    >
      <div className="max-w-xl">

        <div className="flex items-center gap-6">

          <div
            className="
              text-7xl
              font-black
              text-slate-200
            "
          >
            {step.number}
          </div>

          <div>

            <h3
              className="
                text-4xl
                font-bold
                text-[#1E3A5F]
              "
            >
              {step.title}
            </h3>

            <p
              className="
                mt-3
                text-lg
                text-slate-600
              "
            >
              {step.description}
            </p>

          </div>

        </div>

        <div
          className={`
            mt-6
            h-[3px]
            bg-gradient-to-r
            ${
              index % 2 === 0
                ? "from-[#1E3A5F] to-transparent"
                : "from-transparent to-[#1E3A5F]"
            }
          `}
        />

      </div>
    </motion.div>
  ))}

</div>

        {/* Tablet + Mobile */}

        <div className="lg:hidden mt-14 space-y-4">

          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{
                opacity: 0,
                y: 20,
              }}
              whileInView={{
                opacity: 1,
                y: 0,
              }}
              viewport={{ once: true }}
              transition={{
                delay: index * 0.1,
              }}
              className="
                bg-white/80
                backdrop-blur-md
                border
                border-slate-200
                rounded-3xl
                p-6
                shadow-md
              "
            >
              <div
                className="
                  w-10
                  h-10
                  rounded-full
                  bg-[#1E3A5F]
                  text-white
                  flex
                  items-center
                  justify-center
                  font-bold
                "
              >
                {step.number}
              </div>

              <h3 className="mt-4 text-2xl font-bold text-[#1E3A5F]">
                {step.title}
              </h3>

              <p className="mt-3 text-slate-600">
                {step.description}
              </p>
            </motion.div>
          ))}

        </div>

      </div>

    </section>
  );
}