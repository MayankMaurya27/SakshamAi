import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { User, BookOpen, Eye, Headphones, ArrowRight } from "lucide-react";
import Badge from "../ui/Badge";
import Button from "../ui/Button";

const profiles = [
  {
    icon: User,
    id: "beginner",
    title: "Beginner Learners",
    description:
      "Concepts simplified with clear examples, step-by-step explanations, and guided learning support.",
    example: "Plants use sunlight, water, and air to make their food.",
  },
  {
    icon: BookOpen,
    id: "dyslexia",
    title: "Dyslexia Support",
    description:
      "Shorter content blocks, improved readability, reduced complexity, and structured presentation.",
    example:
      "Plants make food from sunlight. This is called photosynthesis.",
  },
  {
    icon: Eye,
    id: "visual",
    title: "Visually Impaired",
    description:
      "Browser narration with play/pause/volume controls, screen-reader friendly content, and inclusive delivery.",
    example: "Content optimized for narration and auditory consumption.",
  },
];

export default function AccessibilitySection() {
  return (
    <section id="accessibility" className="py-20 lg:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <Badge variant="accent">Accessibility First</Badge>
          <h2 className="font-display text-4xl md:text-5xl text-ink mt-4">
            Learning for everyone
          </h2>
          <p className="mt-4 text-ink-muted text-lg">
            The same knowledge, adapted for different learning needs — because
            education should never leave anyone behind.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mt-14">
          {profiles.map((profile, index) => {
            const Icon = profile.icon;
            return (
              <motion.div
                key={profile.id}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="glass-panel-strong rounded-2xl p-7 hover:shadow-elevated transition-all duration-300 hover:-translate-y-1 neural-border"
              >
                <div className="w-12 h-12 rounded-2xl bg-accent/15 text-accent flex items-center justify-center">
                  <Icon size={22} />
                </div>
                <h3 className="mt-5 text-xl font-bold text-ink">
                  {profile.title}
                </h3>
                <p className="mt-3 text-sm text-ink-muted leading-relaxed">
                  {profile.description}
                </p>
                <div className="mt-5 p-4 rounded-xl bg-surface border border-border text-sm text-ink leading-relaxed">
                  {profile.example}
                </div>
                <Link
                  to={`/learn?profile=${profile.id}`}
                  className="mt-5 inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:text-primary transition-colors"
                >
                  Try this profile
                  <ArrowRight size={14} />
                </Link>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-12 neural-border rounded-3xl p-8 lg:p-10 glass-panel-strong"
        >
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-2xl bg-neural/15 text-neural flex items-center justify-center shrink-0">
                <Headphones size={22} />
              </div>
              <div>
                <h3 className="text-xl font-bold text-ink">
                  Browser narration built in
                </h3>
                <p className="mt-2 text-ink-muted text-sm max-w-lg">
                  Read aloud runs entirely in your browser — play, pause, volume,
                  and speed controls. No server audio needed.
                </p>
              </div>
            </div>
            <Button to="/accessibility" variant="secondary" icon={ArrowRight}>
              Learn More
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
