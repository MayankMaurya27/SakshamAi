import { motion } from "framer-motion";
import { Lightbulb, Dumbbell, RefreshCw, Trophy } from "lucide-react";
import Badge from "../ui/Badge";

const steps = [
  {
    number: "01",
    icon: Lightbulb,
    title: "Understand",
    description:
      "Ask questions and receive curriculum-aware explanations tailored to your learning level and accessibility profile.",
    color: "accent",
  },
  {
    number: "02",
    icon: Dumbbell,
    title: "Practice",
    description:
      "Strengthen concepts through AI-generated quizzes and guided exercises that adapt to your progress.",
    color: "neural",
  },
  {
    number: "03",
    icon: RefreshCw,
    title: "Revise",
    description:
      "Create smart summaries, simplified notes, and multilingual content for faster exam preparation.",
    color: "gold",
  },
  {
    number: "04",
    icon: Trophy,
    title: "Assess",
    description:
      "Evaluate understanding with instant feedback, score tracking, and insights into your learning journey.",
    color: "primary",
  },
];

export default function LearningModes() {
  return (
    <section id="journey" className="py-20 lg:py-28 relative">
      <div className="absolute inset-0 bg-gradient-to-b from-accent/3 via-transparent to-primary/3 pointer-events-none" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <Badge variant="gold">Student Journey</Badge>
          <h2 className="font-display text-4xl md:text-5xl text-ink mt-4">
            How learning progresses
          </h2>
          <p className="mt-4 text-ink-muted text-lg">
            Saksham AI guides you through every stage — from first curiosity
            to confident mastery.
          </p>
        </div>

        <div className="mt-16 grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative group"
              >
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-12 left-[calc(100%+4px)] w-[calc(100%-8px)] h-px bg-gradient-to-r from-border-strong to-transparent z-0" />
                )}
                <div className="glass-panel-strong rounded-2xl p-6 h-full transition-all duration-300 group-hover:shadow-elevated group-hover:-translate-y-1">
                  <div className="flex items-center justify-between">
                    <div
                      className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                        step.color === "accent"
                          ? "bg-accent/15 text-accent"
                          : step.color === "neural"
                            ? "bg-neural/15 text-neural"
                            : step.color === "gold"
                              ? "bg-gold/15 text-gold"
                              : "bg-primary/10 text-primary"
                      }`}
                    >
                      <Icon size={22} />
                    </div>
                    <span className="text-4xl font-black text-primary/8 font-display">
                      {step.number}
                    </span>
                  </div>
                  <h3 className="mt-5 text-xl font-bold text-ink">
                    {step.title}
                  </h3>
                  <p className="mt-3 text-sm text-ink-muted leading-relaxed">
                    {step.description}
                  </p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
