import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

const nodes = [
  {
    title: "Learn",
    desc: "Understand concepts clearly",
  },
  {
    title: "Quiz",
    desc: "Practice and test knowledge",
  },
  {
    title: "Notes",
    desc: "Quick revision material",
  },
  {
    title: "Accessibility",
    desc: "Support for every learner",
  },
  {
    title: "Curriculum AI",
    desc: "Aligned with school syllabus",
  },
  {
    title: "Offline AI",
    desc: "Works without cloud dependency",
  },
];

export default function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center">
      <div className="max-w-7xl mx-auto px-6 py-24 w-full">

        {/* Badge */}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex justify-center"
        >
          <div
            className="
              inline-flex
              items-center
              gap-2
              rounded-full
              bg-white/80
              backdrop-blur-md
              border
              border-slate-200
              px-5
              py-2
              text-sm
              text-slate-600
              shadow-sm
            "
          >
            <Sparkles size={14} />
            Offline • Accessible • Curriculum Aware
          </div>
        </motion.div>

        {/* Heading */}

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
          className="text-center mt-10"
        >
          <h1
            className="
              text-5xl
              md:text-7xl
              lg:text-8xl
              font-black
              tracking-tight
              text-[#1E3A5F]
            "
          >
            Saksham AI
          </h1>

          <p
            className="
              mt-5
              text-lg
              md:text-xl
              text-slate-600
              max-w-2xl
              mx-auto
            "
          >
            Learning Without Barriers
          </p>
        </motion.div>

        {/* Ecosystem */}

        <div className="mt-20 max-w-4xl mx-auto">

          <div
            className="
              grid
              grid-cols-1
              sm:grid-cols-2
              lg:grid-cols-3
              gap-5
            "
          >
            {nodes.map((node, index) => (
              <motion.div
                key={node.title}
                initial={{
                  opacity: 0,
                  y: 30,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                transition={{
                  delay: index * 0.08,
                }}
                whileHover={{
                  y: -6,
                  scale: 1.03,
                }}
                className="
                  group
                  bg-white/70
                  backdrop-blur-md
                  border
                  border-slate-200
                  rounded-3xl
                  p-6
                  text-center
                  shadow-sm
                  hover:shadow-xl
                  transition-all
                "
              >
                <h3
                  className="
                    text-xl
                    font-bold
                    text-[#1E3A5F]
                  "
                >
                  {node.title}
                </h3>

                <p
                  className="
                    mt-3
                    text-sm
                    text-slate-600
                  "
                >
                  {node.desc}
                </p>
              </motion.div>
            ))}
          </div>

        </div>

        {/* Mission */}

        <motion.div
          initial={{
            opacity: 0,
          }}
          animate={{
            opacity: 1,
          }}
          transition={{
            delay: 0.5,
          }}
          className="
            mt-16
            text-center
          "
        >
          <p
            className="
              text-slate-600
              max-w-3xl
              mx-auto
              leading-relaxed
            "
          >
            Saksham AI combines curriculum-aware learning,
            accessibility support, offline intelligence,
            summaries, quizzes, and multilingual assistance
            into one learning ecosystem designed for every student.
          </p>
        </motion.div>

        {/* CTA */}

        <motion.div
          initial={{
            opacity: 0,
            y: 20,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            delay: 0.6,
          }}
          className="
            mt-12
            flex
            justify-center
          "
        >
          <button
            onClick={() => {
              window.location.href = "/learn";
            }}
            className="
              flex
              items-center
              gap-2
              px-8
              py-4
              rounded-2xl
              bg-[#1E3A5F]
              text-white
              font-semibold
              shadow-lg
              hover:-translate-y-1
              transition-all
            "
          >
            Enter Workspace
            <ArrowRight size={18} />
          </button>
        </motion.div>

      </div>
    </section>
  );
}