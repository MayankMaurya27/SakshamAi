import { motion } from "framer-motion";
import {
  ArrowRight,
  BookMarked,
  Brain,
  BookOpen,
  Accessibility,
  FileText,
  Orbit,
  WifiOff,
} from "lucide-react";

import Badge from "../ui/Badge";
import Button from "../ui/Button";

const features = [
  { icon: Brain, title: "Adaptive", desc: "Profile-aware explanations" },
  { icon: BookOpen, title: "Curriculum", desc: "NCERT Classes 6–10" },
  { icon: FileText, title: "Your Notes", desc: "Upload & learn from PDFs" },
  { icon: Orbit, title: "Concept Maps", desc: "Visual chapter graphs" },
  { icon: Accessibility, title: "Inclusive", desc: "Every learner supported" },
  { icon: WifiOff, title: "Offline Ready", desc: "Edge-first design" },
];

export default function HeroSection() {
  return (
    <section className="relative min-h-[92vh] flex items-center overflow-hidden">
      {/* Background Orbs */}
      <div className="aurora-orb w-[500px] h-[500px] -top-32 -left-48 bg-primary/12" />
      <div className="aurora-orb w-[400px] h-[400px] top-1/3 -right-40 bg-accent/10" />
      <div className="aurora-orb w-[300px] h-[300px] bottom-0 left-1/3 bg-neural/8" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-28 w-full">
        {/* Hero Layout */}
        <div className="grid lg:grid-cols-2 gap-14 lg:gap-20 items-center">
          
          {/* Left Content */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
          >
            <Badge variant="gold">
              <BookMarked size={12} />
              EDGE MINDS · Saksham
            </Badge>

            <h1 className="mt-8 font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-ink leading-[1.05] tracking-tight">
              Learning that{" "}
              <span className="gradient-text italic">
                adapts
              </span>
              <br />
              to every mind
            </h1>

            <p className="mt-6 text-base sm:text-lg md:text-xl text-ink-muted max-w-xl leading-relaxed">
              Saksham turns your study materials into a living workspace —
              concept maps, quizzes, summaries, and narration built for real
              classrooms.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mt-10">
              <Button to="/learn" size="lg" icon={ArrowRight}>
                Enter Workspace
              </Button>

              <Button
                to="/upload"
                variant="secondary"
                size="lg"
                icon={FileText}
              >
                Upload Notes
              </Button>
            </div>
          </motion.div>

          {/* Right Visual */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="relative"
          >
            <div className="glass-panel rounded-3xl p-8 h-[450px] neural-border relative overflow-hidden">

              <div className="flex justify-between items-center">
                <span className="text-sm text-ink-muted">
                  Active Learning Session
                </span>

                <Badge variant="gold">
                  AI Powered
                </Badge>
              </div>

              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  animate={{ scale: [1, 1.05, 1] }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                  }}
                  className="w-44 h-44 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center"
                >
                  <Brain
                    size={80}
                    className="text-primary"
                  />
                </motion.div>
              </div>

              {/* Floating Cards */}

              <motion.div
                animate={{ y: [-5, 5, -5] }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                }}
                className="absolute top-20 right-8 glass-panel px-4 py-3 rounded-2xl"
              >
                <div className="text-xs text-ink-muted">
                  Generated
                </div>
                <div className="text-sm font-semibold">
                  Quiz Ready
                </div>
              </motion.div>

              <motion.div
                animate={{ y: [5, -5, 5] }}
                transition={{
                  duration: 3.5,
                  repeat: Infinity,
                }}
                className="absolute bottom-20 left-6 glass-panel px-4 py-3 rounded-2xl"
              >
                <div className="text-xs text-ink-muted">
                  Visual Learning
                </div>
                <div className="text-sm font-semibold">
                  Concept Map
                </div>
              </motion.div>

              <motion.div
                animate={{ y: [-4, 4, -4] }}
                transition={{
                  duration: 2.8,
                  repeat: Infinity,
                }}
                className="absolute top-1/2 -translate-y-1/2 left-0 glass-panel px-4 py-3 rounded-2xl"
              >
                <div className="text-xs text-ink-muted">
                  Uploaded
                </div>
                <div className="text-sm font-semibold">
                  PDF Notes
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{
            duration: 0.8,
            delay: 0.4,
          }}
          className="mt-20 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4"
        >
          {features.map((feature, i) => {
            const Icon = feature.icon;

            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  delay: 0.5 + i * 0.06,
                }}
                whileHover={{ y: -4 }}
                className="glass-panel rounded-2xl p-4 sm:p-5 text-center group cursor-default neural-border"
              >
                <div className="w-10 h-10 mx-auto rounded-xl bg-primary/12 flex items-center justify-center text-primary group-hover:bg-accent/15 group-hover:text-accent transition-colors">
                  <Icon size={20} />
                </div>

                <h3 className="mt-3 text-sm font-bold text-ink">
                  {feature.title}
                </h3>

                <p className="mt-1 text-xs text-ink-muted hidden sm:block">
                  {feature.desc}
                </p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}