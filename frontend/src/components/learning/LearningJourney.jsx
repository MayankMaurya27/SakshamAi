import { motion } from "framer-motion";
import {
  BookOpen,
  WifiOff,
  Accessibility,
  Languages,
  Brain,
  ArrowRight,
} from "lucide-react";
import Badge from "../ui/Badge";
import Button from "../ui/Button";

const pillars = [
  {
    icon: BookOpen,
    title: "Curriculum Aware",
    description:
      "Aligned with school syllabus and educational content — not generic internet answers.",
  },
  {
    icon: WifiOff,
    title: "Offline First",
    description:
      "Designed to function in low-connectivity environments with local AI processing.",
  },
  {
    icon: Accessibility,
    title: "Accessible Learning",
    description:
      "Supports beginner learners, dyslexic learners, and visually impaired students.",
  },
  {
    icon: Languages,
    title: "Multilingual Support",
    description:
      "Learning experiences adapted into Hindi and Hinenglish for broader reach.",
  },
  {
    icon: Brain,
    title: "Personalized Understanding",
    description:
      "Explanations adapt to different learning levels, profiles, and needs.",
  },
];

export default function LearningJourney() {
  return (
    <section id="why-saksham" className="py-20 lg:py-28 relative">
      <div className="absolute inset-0 bg-gradient-to-t from-primary/4 to-transparent pointer-events-none" />
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <Badge variant="primary">Why Saksham</Badge>
          <h2 className="font-display text-4xl md:text-5xl text-ink mt-4">
            Built for real learning
          </h2>
          <p className="mt-4 text-ink-muted text-lg">
            Purpose-built for education, accessibility, and curriculum-aware
            intelligence — not general-purpose chat.
          </p>
        </div>

        <div className="mt-16 space-y-0">
          {pillars.map((pillar, index) => {
            const Icon = pillar.icon;
            return (
              <motion.div
                key={pillar.title}
                initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08 }}
                className="group py-8 border-b border-border last:border-0"
              >
                <div className="grid lg:grid-cols-[80px_1fr_auto] gap-6 items-center">
                  <div className="text-5xl font-black text-primary/15 font-display hidden lg:block">
                    {String(index + 1).padStart(2, "0")}
                  </div>
                  <div className="flex items-start gap-5">
                    <div className="w-11 h-11 rounded-xl bg-accent/10 text-accent flex items-center justify-center shrink-0 group-hover:bg-primary group-hover:text-void transition-colors">
                      <Icon size={20} />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-ink">
                        {pillar.title}
                      </h3>
                      <p className="mt-2 text-ink-muted leading-relaxed max-w-2xl">
                        {pillar.description}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 text-center"
        >
          <div className="neural-border rounded-3xl p-10 lg:p-14 glass-panel-strong">
            <h3 className="font-display text-3xl md:text-4xl text-ink">
              Ready to learn differently?
            </h3>
            <p className="mt-4 text-ink-muted max-w-lg mx-auto">
              Upload your notes and let Saksham guide your journey through
              every chapter.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8">
              <Button to="/learn" size="lg" icon={ArrowRight}>
                Start Learning
              </Button>
              <Button to="/dashboard" variant="secondary" size="lg">
                View Dashboard
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
