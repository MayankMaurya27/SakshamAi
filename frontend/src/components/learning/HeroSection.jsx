import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

export default function HeroSection() {
  const headlines = [
    "Understand Better.",
    "Think Deeper.",
    "Practice Smarter.",
    "Build Confidence.",
    "Keep Learning.",
  ];

  const placeholders = [
    "Ask a question...",
    "Upload your notes...",
    "Generate a quiz...",
    "Create a revision sheet...",
    "Learn in your language...",
  ];

  const [currentHeadline, setCurrentHeadline] = useState(0);
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);

  useEffect(() => {
    const headlineInterval = setInterval(() => {
      setCurrentHeadline(
        (prev) => (prev + 1) % headlines.length
      );
    }, 3000);

    return () => clearInterval(headlineInterval);
  }, []);

  useEffect(() => {
    const placeholderInterval = setInterval(() => {
      setCurrentPlaceholder(
        (prev) => (prev + 1) % placeholders.length
      );
    }, 2500);

    return () => clearInterval(placeholderInterval);
  }, []);

  return (
    <section className="relative overflow-hidden">

      {/* Background Glow */}

      <div
        className="
          absolute
          inset-0
          -z-10
          overflow-hidden
        "
      >
        <div
          className="
            absolute
            top-20
            left-1/2
            -translate-x-1/2
            h-[500px]
            w-[500px]
            rounded-full
            bg-blue-200/30
            blur-[140px]
          "
        />

        <div
          className="
            absolute
            bottom-0
            right-0
            h-[350px]
            w-[350px]
            rounded-full
            bg-green-200/20
            blur-[120px]
          "
        />

      </div>

      <div className="max-w-7xl mx-auto px-6 pt-20 pb-28">

        {/* Badge */}

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center"
        >
          <div
            className="
              inline-flex
              items-center
              gap-2
              rounded-full
              border
              border-slate-200
              bg-white/80
              backdrop-blur-md
              px-5
              py-2.5
              text-sm
              font-medium
              text-slate-600
              shadow-sm
            "
          >
            Offline AI • Curriculum Aware • Accessibility First
          </div>
        </motion.div>

        {/* Heading */}

        <div className="mt-14 text-center">

          <motion.h1
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="
              text-6xl
              md:text-8xl
              font-black
              tracking-tight
              text-[#1E3A5F]
            "
          >
            Let's
          </motion.h1>

          <div className="h-[90px] md:h-[120px] mt-4">

            <AnimatePresence mode="wait">

              <motion.div
                key={headlines[currentHeadline]}
                initial={{
                  opacity: 0,
                  y: 25,
                }}
                animate={{
                  opacity: 1,
                  y: 0,
                }}
                exit={{
                  opacity: 0,
                  y: -25,
                }}
                transition={{
                  duration: 0.45,
                }}
                className="
                  text-4xl
                  md:text-7xl
                  font-bold
                  text-[#256D5A]
                "
              >
                {headlines[currentHeadline]}
              </motion.div>

            </AnimatePresence>

          </div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{
              delay: 0.2,
            }}
            className="
              mt-6
              max-w-3xl
              mx-auto
              text-lg
              md:text-xl
              text-slate-600
              leading-relaxed
            "
          >
            An accessible learning workspace
            designed to help students understand
            concepts, strengthen knowledge and
            learn with confidence.
          </motion.p>

        </div>

        {/* Search Box */}

        <motion.div
          initial={{
            opacity: 0,
            y: 25,
          }}
          animate={{
            opacity: 1,
            y: 0,
          }}
          transition={{
            delay: 0.3,
          }}
          className="mt-14"
        >

          <div
            className="
              max-w-4xl
              mx-auto
              bg-white/90
              backdrop-blur-md
              border
              border-slate-200
              rounded-[32px]
              shadow-xl
              p-4
            "
          >

            <input
              type="text"
              placeholder={
                placeholders[currentPlaceholder]
              }
              className="
                w-full
                bg-transparent
                px-4
                py-4
                text-lg
                outline-none
              "
            />

          </div>

        </motion.div>

        {/* Quick Actions */}

        <motion.div
          initial={{
            opacity: 0,
          }}
          animate={{
            opacity: 1,
          }}
          transition={{
            delay: 0.4,
          }}
          className="
            mt-8
            flex
            flex-wrap
            justify-center
            gap-3
          "
        >

          {[
            "Understand",
            "Practice",
            "Revise",
            "Quiz",
            "Accessibility",
          ].map((item) => (
            <button
              key={item}
              className="
                rounded-full
                bg-white
                border
                border-slate-200
                px-5
                py-2.5
                text-sm
                font-medium
                shadow-sm
                hover:shadow-md
                hover:-translate-y-1
                transition-all
              "
            >
              {item}
            </button>
          ))}

        </motion.div>

      </div>

    </section>
  );
}