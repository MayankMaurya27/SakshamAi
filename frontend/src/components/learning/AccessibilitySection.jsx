import { motion } from "framer-motion";
import {
  Languages,
  Volume2,
  Eye,
  Type,
} from "lucide-react";

const features = [
  {
    icon: Languages,
    title: "Multilingual Learning",
    description:
      "Learn in your preferred language with localized explanations.",
  },
  {
    icon: Volume2,
    title: "Audio Support",
    description:
      "Listen to explanations for a more accessible learning experience.",
  },
  {
    icon: Eye,
    title: "High Contrast Mode",
    description:
      "Improve readability with enhanced visual accessibility.",
  },
  {
    icon: Type,
    title: "Reading Assistance",
    description:
      "Optimized typography and accessibility-focused design.",
  },
];

export default function AccessibilitySection() {
  return (
    <section className="py-28">

      <div className="max-w-7xl mx-auto px-6">

        <div className="text-center">

          <p className="uppercase tracking-[0.3em] text-sm text-slate-500">
            Accessibility First
          </p>

          <h2 className="mt-4 text-5xl font-bold text-[#1E3A5F]">
            Learning For Everyone
          </h2>

          <p className="mt-6 max-w-2xl mx-auto text-slate-600 text-lg">
            Saksham AI is designed to make learning more
            inclusive, accessible and adaptable.
          </p>

        </div>

        <div className="grid md:grid-cols-2 gap-8 mt-20">

          {features.map((feature, index) => {
            const Icon = feature.icon;

            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{
                  delay: index * 0.1,
                }}
                className="
                  bg-white
                  border
                  border-slate-200
                  rounded-[32px]
                  p-8
                  shadow-lg
                  hover:-translate-y-1
                  transition-all
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
                  {feature.title}
                </h3>

                <p className="mt-3 text-slate-600 leading-relaxed">
                  {feature.description}
                </p>

              </motion.div>
            );
          })}

        </div>

      </div>

    </section>
  );
}