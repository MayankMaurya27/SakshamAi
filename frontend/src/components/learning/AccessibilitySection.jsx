import { motion } from "framer-motion";
import {
  User,
  BookOpen,
  Eye,
  Headphones,
} from "lucide-react";

const profiles = [
  {
    icon: User,
    title: "Beginner Learners",
    description:
      "Concepts are simplified into easy-to-understand explanations with examples and guided learning support.",
  },
  {
    icon: BookOpen,
    title: "Dyslexic Support",
    description:
      "Structured content, reduced reading complexity and learner-friendly presentation improve accessibility.",
  },
  {
    icon: Eye,
    title: "Visually Impaired",
    description:
      "Accessible content delivery with narration support and inclusive learning experiences.",
  },
];

export default function AccessibilitySection() {
  return (
    <section id="accessibility" className="py-20">

      <div className="max-w-7xl mx-auto px-6">

        {/* Heading */}

        <div className="text-center">

          <p className="uppercase tracking-[0.35em] text-sm text-slate-500">
            Accessibility First
          </p>

          <h2 className="mt-4 text-4xl md:text-6xl font-bold text-[#1E3A5F]">
            Learning For Everyone
          </h2>

          <p className="mt-6 max-w-3xl mx-auto text-slate-600 text-lg">
            Saksham AI adapts the same educational content for
            different learning needs, ensuring every student
            can learn effectively.
          </p>

        </div>

        {/* Accessibility Profiles */}

        <div className="grid lg:grid-cols-3 gap-8 mt-16">

          {profiles.map((profile, index) => {
            const Icon = profile.icon;

            return (
              <motion.div
                key={profile.title}
                initial={{
                  opacity: 0,
                  y: 30,
                }}
                whileInView={{
                  opacity: 1,
                  y: 0,
                }}
                viewport={{ once: true }}
                transition={{
                  delay: index * 0.15,
                }}
                whileHover={{
                  y: -8,
                }}
                className="
                  bg-white/80
                  backdrop-blur-md
                  border
                  border-slate-200
                  rounded-[32px]
                  p-8
                  shadow-lg
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
                  <Icon size={24} />
                </div>

                <h3 className="mt-6 text-2xl font-bold text-[#1E3A5F]">
                  {profile.title}
                </h3>

                <p className="mt-4 text-slate-600 leading-relaxed">
                  {profile.description}
                </p>

              </motion.div>
            );
          })}

        </div>

        {/* Example Card */}

        <motion.div
          initial={{
            opacity: 0,
            y: 30,
          }}
          whileInView={{
            opacity: 1,
            y: 0,
          }}
          viewport={{ once: true }}
          className="
            mt-16
            bg-white/80
            backdrop-blur-md
            border
            border-slate-200
            rounded-[32px]
            p-8
            shadow-lg
          "
        >

          <div className="flex items-center gap-3">
            <Headphones className="text-[#1E3A5F]" />
            <h3 className="text-2xl font-bold text-[#1E3A5F]">
              Adaptive Learning Experience
            </h3>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mt-8">

            <div className="bg-slate-50 rounded-2xl p-5 border">
              <div className="font-semibold text-[#1E3A5F]">
                Beginner
              </div>

              <p className="mt-3 text-slate-600 text-sm">
                Plants use sunlight, water and air to make their food.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-5 border">
              <div className="font-semibold text-[#1E3A5F]">
                Dyslexic Friendly
              </div>

              <p className="mt-3 text-slate-600 text-sm">
                Shorter content blocks with improved readability and reduced complexity.
              </p>
            </div>

            <div className="bg-slate-50 rounded-2xl p-5 border">
              <div className="font-semibold text-[#1E3A5F]">
                Audio Support
              </div>

              <p className="mt-3 text-slate-600 text-sm">
                Content can be narrated and consumed through audio.
              </p>
            </div>

          </div>

        </motion.div>

      </div>

    </section>
  );
}