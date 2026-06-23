import { motion } from "framer-motion";
import {
  BookOpen,
  WifiOff,
  Accessibility,
  Languages,
  Brain,
} from "lucide-react";

const pillars = [
  {
    icon: BookOpen,
    title: "Curriculum Aware",
    description:
      "Aligned with school curriculum and educational content rather than generic internet answers.",
  },
  {
    icon: WifiOff,
    title: "Offline First",
    description:
      "Designed to function even in low-connectivity environments.",
  },
  {
    icon: Accessibility,
    title: "Accessible Learning",
    description:
      "Supports beginner learners, dyslexic learners and visually impaired students.",
  },
  {
    icon: Languages,
    title: "Multilingual Support",
    description:
      "Learning experiences can be adapted into different languages.",
  },
  {
    icon: Brain,
    title: "Personalized Understanding",
    description:
      "Explanations adapt to different learning levels and needs.",
  },
];

export default function LearningJourney() {
  return (
    <section id="learning-journey" className="py-20">

      <div className="max-w-7xl mx-auto px-6">

        <div className="text-center">

          <p className="uppercase tracking-[0.35em] text-sm text-slate-500">
            Why Saksham AI
          </p>

          <h2 className="mt-4 text-4xl md:text-6xl font-bold text-[#1E3A5F]">
            Built For Real Learning
          </h2>

          <p className="mt-6 max-w-3xl mx-auto text-slate-600 text-lg">
            Saksham AI is designed specifically for education,
            accessibility and curriculum-aware learning rather than
            general-purpose conversation.
          </p>

        </div>

        <div className="mt-20">

  {pillars.map((pillar, index) => (
    <motion.div
      key={pillar.title}
      initial={{
        opacity: 0,
        y: 40,
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
        py-12
        border-b
        border-slate-200
      "
    >

      <div className="grid lg:grid-cols-[120px_1fr] gap-8 items-start">

        <div
          className="
            text-5xl
            md:text-6xl
            font-black
            text-slate-200
          "
        >
          {String(index + 1).padStart(2, "0")}
        </div>

        <div>

          <h3
            className="
              text-3xl
              md:text-5xl
              font-bold
              text-[#1E3A5F]
            "
          >
            {pillar.title}
          </h3>

          <p
            className="
              mt-4
              max-w-3xl
              text-lg
              text-slate-600
              leading-relaxed
            "
          >
            {pillar.description}
          </p>

        </div>

      </div>

    </motion.div>
  ))}

</div>

      </div>

    </section>
  );
}