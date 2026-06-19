import { motion } from "framer-motion";

const journey = [
  {
    step: "01",
    title: "Ask",
    description: "Start with any doubt, concept or topic from your curriculum.",
  },
  {
    step: "02",
    title: "Understand",
    description: "Receive explanations adapted to your learning level.",
  },
  {
    step: "03",
    title: "Practice",
    description: "Generate quizzes and reinforce your understanding.",
  },
  {
    step: "04",
    title: "Revise",
    description: "Turn concepts into summaries and revision material.",
  },
  {
    step: "05",
    title: "Grow",
    description: "Build confidence through continuous learning.",
  },
];

export default function LearningJourney() {
  return (
    <section className="py-32 relative">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center">
          <p className="uppercase tracking-[0.3em] text-slate-500 text-sm">
            Learning Journey
          </p>

          <h2 className="mt-5 text-5xl font-bold text-[#1E3A5F]">
            Every Question Has A Path
          </h2>
        </div>

        <div className="mt-24 relative">
          <div
            className="
    absolute
    left-1/2
    top-10
    bottom-10
    w-[3px]
    bg-gradient-to-b
    from-slate-200
    via-[#1E3A5F]
    to-slate-200
    -translate-x-1/2
    hidden md:block
  "
          />

          <div className="space-y-16">
            {journey.map((item, index) => (
              <motion.div
                key={item.step}
                initial={{
                  opacity: 0,
                  y: 50,
                }}
                whileInView={{
                  opacity: 1,
                  y: 0,
                }}
                viewport={{
                  once: true,
                }}
                transition={{
                  duration: 0.5,
                  delay: index * 0.15,
                }}
                className={`
                  flex
                  items-center
                  gap-10
                  ${index % 2 === 0 ? "md:flex-row" : "md:flex-row-reverse"}
                `}
              >
                <div className="flex-1">
                  <div
                    className="
                      bg-white
                      border
                      border-slate-200
                      rounded-[28px]
                      p-8
                      shadow-lg
                    "
                  >
                    <span className="text-sm text-slate-500">{item.step}</span>

                    <h3
                      className="
                        mt-2
                        text-3xl
                        font-bold
                        text-[#1E3A5F]
                      "
                    >
                      {item.title}
                    </h3>

                    <p
                      className="
                        mt-4
                        text-slate-600
                        leading-relaxed
                      "
                    >
                      {item.description}
                    </p>
                  </div>
                </div>

                <div
  className="
    hidden
    md:flex
    w-16
    h-16
    rounded-full
    bg-[#1E3A5F]
    text-white
    shadow-xl
    items-center
    justify-center
    font-bold
    text-lg
    shrink-0
    z-10
  "
>
  {item.step}
</div>

                <div className="flex-1" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
