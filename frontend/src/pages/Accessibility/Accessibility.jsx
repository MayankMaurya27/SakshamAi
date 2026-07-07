import { useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  BookOpen,
  Eye,
  Headphones,
  Type,
  Contrast,
  Volume2,
  ArrowRight,
  CheckCircle2,
  Mic,
  MicOff,
  Terminal,
  VolumeX,
} from "lucide-react";
import MainLayout from "../../components/layout/MainLayout";
import PageHeader from "../../components/ui/PageHeader";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Badge from "../../components/ui/Badge";
import AudioPlayer from "../../components/audio/AudioPlayer";
import KnowledgeBackground from "../../components/background/KnowledgeBackground";
import { useSpeechPlayer } from "../../hooks/useSpeechPlayer";
import { useVoiceAssistant } from "../../hooks/useVoiceAssistant";

const profiles = [
  {
    id: "beginner",
    icon: User,
    title: "Beginner Learners",
    description:
      "Delivers direct, structured, and curriculum-accurate textbook answers. Perfect for standard syllabus-aligned study, keeping explanations precise and clear.",
    features: [
      "Syllabus-aligned answers",
      "Structured explanations",
      "Direct factual context",
      "Curriculum focus",
    ],
    example: {
      question: "What is photosynthesis?",
      answer:
        "Plants use sunlight, water, and air to make their food. This process is called photosynthesis. The green color in leaves helps capture sunlight.",
    },
  },
  {
    id: "dyslexia",
    icon: BookOpen,
    title: "Dyslexia Support",
    description:
      "Structured content with reduced reading complexity, shorter paragraphs, and learner-friendly presentation that improves readability and comprehension.",
    features: [
      "Shorter content blocks",
      "Reduced complexity",
      "Structured layout",
      "Improved readability",
    ],
    example: {
      question: "What is photosynthesis?",
      answer:
        "Plants make food from sunlight.\n\nThis is photosynthesis.\n\nGreen leaves capture the light.\n\nWater and air help too.",
    },
  },
  {
    id: "visual",
    icon: Eye,
    title: "Visually Impaired",
    description:
      "Browser-based narration with full playback controls, screen reader friendly content, and inclusive delivery for all students.",
    features: [
      "Play / pause / stop controls",
      "Volume & speed adjustment",
      "Screen reader friendly",
      "No server audio required",
    ],
    example: {
      question: "What is photosynthesis?",
      answer:
        "Photosynthesis is how plants create food. They use energy from sunlight, combined with water from soil and carbon dioxide from air, to produce glucose and release oxygen.",
    },
  },
];

const accessibilityFeatures = [
  { icon: Type, title: "Readable Typography", desc: "Sora + Fraunces fonts" },
  { icon: Contrast, title: "High Contrast", desc: "Aurora dark theme" },
  { icon: Volume2, title: "Read Aloud", desc: "Browser TTS with controls" },
  { icon: Headphones, title: "Audio Player", desc: "Play, pause, volume, speed" },
];

const DEMO_TEXT =
  "Photosynthesis is how plants create food. They use energy from sunlight, combined with water and carbon dioxide, to produce glucose and release oxygen.";

export default function Accessibility() {
  const speech = useSpeechPlayer();
  const voice = useVoiceAssistant();
  const [demoProfile, setDemoProfile] = useState(profiles[2]);

  return (
    <MainLayout>
      <KnowledgeBackground intensity="subtle" />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        <PageHeader
          eyebrow="Inclusive Design"
          title="Accessibility Center"
          description="Saksham adapts the same educational content for different learning needs — with built-in browser narration that needs no backend."
          align="center"
        />

        <Card className="mt-10 neural-border">
          <div className="flex flex-col lg:flex-row gap-8">
            <div className="flex-1">
              <Badge variant="accent">Live Demo</Badge>
              <h3 className="text-xl font-bold text-ink mt-3">
                Try the audio player
              </h3>
              <p className="mt-2 text-sm text-ink-muted leading-relaxed">
                All narration runs in your browser using the Web Speech API.
                Adjust volume, speed, and pause anytime — no server calls.
              </p>
              <p className="mt-4 text-sm text-ink leading-relaxed bg-surface rounded-xl p-4 border border-border">
                {DEMO_TEXT}
              </p>
            </div>
            <div className="lg:w-[380px] shrink-0">
              <AudioPlayer
                text={DEMO_TEXT}
                status={speech.status}
                volume={speech.volume}
                rate={speech.rate}
                onToggle={speech.toggle}
                onStop={speech.stop}
                onVolumeChange={speech.setVolume}
                onRateChange={speech.setRate}
                label="Demo Narration"
              />
            </div>
          </div>
        </Card>

        {/* Voice Assistant Prototyping Dashboard */}
        <Card className="mt-8 border border-border/80 bg-surface/50">
          <div className="flex flex-col lg:flex-row gap-8">
            <div className="flex-1 flex flex-col justify-between">
              <div>
                <Badge variant={voice.isActive ? "accent" : "secondary"}>
                  {voice.isActive ? "Voice Assistant Active" : "Voice Assistant Disabled"}
                </Badge>
                <h3 className="text-xl font-bold text-ink mt-3">
                  Saksham Voice Assistant (Beta)
                </h3>
                <p className="mt-2 text-sm text-ink-muted leading-relaxed">
                  A conversational tutor helper for visually impaired students. 
                  Press <strong>Spacebar</strong> to talk when active, and <strong>Escape</strong> to stop.
                </p>
                
                {/* Active Context Slots */}
                <div className="grid grid-cols-3 gap-4 mt-6">
                  <div className="p-3 bg-surface rounded-xl border border-border text-center">
                    <p className="text-xs text-ink-muted font-semibold uppercase tracking-wider">Class</p>
                    <p className="mt-1 text-sm font-bold text-ink">{voice.classLevel ? `Class ${voice.classLevel}` : "Not Set"}</p>
                  </div>
                  <div className="p-3 bg-surface rounded-xl border border-border text-center">
                    <p className="text-xs text-ink-muted font-semibold uppercase tracking-wider">Subject</p>
                    <p className="mt-1 text-sm font-bold text-ink truncate">{voice.subject || "Not Set"}</p>
                  </div>
                  <div className="p-3 bg-surface rounded-xl border border-border text-center">
                    <p className="text-xs text-ink-muted font-semibold uppercase tracking-wider">Chapter</p>
                    <p className="mt-1 text-sm font-bold text-ink truncate">{voice.chapter || "Not Set"}</p>
                  </div>
                </div>
                
                {/* Active Task Details (Phase 2 UI update) */}
                {voice.activeTask !== "idle" && (
                  <div className="mt-4 p-4 rounded-xl border border-accent/20 bg-accent/5">
                    <div className="flex justify-between items-center mb-2">
                      <p className="text-xs font-semibold text-accent uppercase tracking-wider">
                        Active Mode: {voice.activeTask === "summary" ? "Summary Reader" : "Active Quiz"}
                      </p>
                      {voice.activeTask === "quiz" && (
                        <p className="text-xs font-bold text-ink bg-surface border border-border px-2 py-0.5 rounded">
                          Score: {voice.quizScore} / {voice.quizQuestions.length}
                        </p>
                      )}
                    </div>
                    {voice.activeTask === "summary" && voice.summaryParagraphs.length > 0 && (
                      <div>
                        <p className="text-sm text-ink font-medium italic leading-relaxed bg-surface/40 p-3 rounded-lg border border-border/50">
                          "{voice.summaryParagraphs[voice.summaryParagraphIdx]}"
                        </p>
                        <p className="text-[10px] text-ink-muted mt-2 font-mono">
                          Paragraph {voice.summaryParagraphIdx + 1} of {voice.summaryParagraphs.length}
                        </p>
                      </div>
                    )}
                    {voice.activeTask === "quiz" && voice.quizQuestions.length > 0 && (
                      <div>
                        <p className="text-sm text-ink font-bold leading-relaxed bg-surface/40 p-3 rounded-lg border border-border/50">
                          Q{voice.quizQuestionIdx + 1}: {voice.quizQuestions[voice.quizQuestionIdx]?.question}
                        </p>
                        <div className="grid grid-cols-2 gap-2 mt-2">
                          {Object.entries(voice.quizQuestions[voice.quizQuestionIdx]?.options || {}).map(([key, val]) => (
                            <div key={key} className="text-xs text-ink-muted border border-border p-1.5 rounded-lg bg-surface">
                              <span className="font-bold text-accent mr-1">{key}:</span> {val}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-6 flex flex-wrap gap-3">
                <Button 
                  onClick={voice.toggleAssistant}
                  variant={voice.isActive ? "secondary" : "primary"}
                  icon={voice.isActive ? MicOff : Mic}
                >
                  {voice.isActive ? "Disable Voice Mode" : "Enable Voice Mode"}
                </Button>
                {voice.isActive && (
                  <Button 
                    onClick={voice.startListening}
                    disabled={voice.status === "listening" || voice.status === "processing"}
                    variant="accent"
                    icon={Mic}
                  >
                    {voice.status === "listening" ? "Listening..." : "Trigger Listen"}
                  </Button>
                )}
                {voice.isActive && (
                  <Button 
                    onClick={voice.stopSpeaking}
                    variant="secondary"
                    icon={VolumeX}
                  >
                    Stop Speaking
                  </Button>
                )}
              </div>
            </div>

            {/* Real-time speech log */}
            <div className="lg:w-[480px] flex flex-col">
              <div className="flex items-center gap-2 text-xs font-semibold text-ink-muted uppercase tracking-wider mb-2">
                <Terminal size={14} className="text-accent" />
                <span>Assistant Logs</span>
              </div>
              <div className="h-48 overflow-y-auto bg-surface rounded-xl border border-border p-4 font-mono text-xs text-ink-muted flex flex-col gap-2">
                {voice.log.length === 0 ? (
                  <p className="italic text-ink-muted/50">Enable voice mode to initialize logs...</p>
                ) : (
                  voice.log.map((item, idx) => (
                    <div key={idx} className="flex gap-2 leading-relaxed">
                      <span className="text-accent shrink-0">[{item.time}]</span>
                      <span className={item.type === "error" ? "text-red-400" : item.type === "success" ? "text-emerald-400" : ""}>
                        {item.text}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </Card>


        <div className="grid lg:grid-cols-3 gap-6 mt-12">
          {profiles.map((profile, index) => {
            const Icon = profile.icon;
            return (
              <motion.div
                key={profile.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card
                  className={`h-full flex flex-col cursor-pointer transition-all ${
                    demoProfile.id === profile.id ? "ring-2 ring-accent" : ""
                  }`}
                  onClick={() => setDemoProfile(profile)}
                >
                  <div className="w-12 h-12 rounded-2xl bg-accent/15 text-accent flex items-center justify-center">
                    <Icon size={22} />
                  </div>
                  <h3 className="mt-5 text-xl font-bold text-ink">
                    {profile.title}
                  </h3>
                  <p className="mt-3 text-sm text-ink-muted leading-relaxed flex-1">
                    {profile.description}
                  </p>

                  <ul className="mt-5 space-y-2">
                    {profile.features.map((f) => (
                      <li
                        key={f}
                        className="flex items-center gap-2 text-sm text-ink"
                      >
                        <CheckCircle2 size={14} className="text-accent shrink-0" />
                        {f}
                      </li>
                    ))}
                  </ul>

                  <div className="mt-5 p-4 rounded-xl bg-surface border border-border">
                    <p className="text-xs font-semibold text-accent uppercase tracking-wider">
                      Example Output
                    </p>
                    <p className="mt-2 text-sm text-ink-muted whitespace-pre-wrap leading-relaxed">
                      {profile.example.answer}
                    </p>
                  </div>

                  <Button
                    to={`/learn?profile=${profile.id}`}
                    variant="secondary"
                    className="mt-5 w-full"
                    icon={ArrowRight}
                  >
                    Try This Profile
                  </Button>
                </Card>
              </motion.div>
            );
          })}
        </div>

        <Card className="mt-12">
          <h2 className="text-xl font-bold text-ink text-center">
            Built-in Accessibility Features
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8">
            {accessibilityFeatures.map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="text-center">
                  <div className="w-11 h-11 mx-auto rounded-xl bg-neural/15 text-neural flex items-center justify-center">
                    <Icon size={20} />
                  </div>
                  <h3 className="mt-3 text-sm font-bold text-ink">
                    {feature.title}
                  </h3>
                  <p className="mt-1 text-xs text-ink-muted">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </Card>

        <div className="mt-12 neural-border rounded-3xl p-8 lg:p-12 glass-panel-strong text-center">
          <Badge variant="accent">How It Works</Badge>
          <h3 className="font-display text-3xl text-ink mt-4">
            One curriculum, three ways to learn
          </h3>
          <p className="mt-4 text-ink-muted max-w-2xl mx-auto">
            Select your learning profile in the workspace. Saksham instantly
            adapts how content is presented — without changing what you learn.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8">
            <Button to="/learn" size="lg" icon={ArrowRight}>
              Open Workspace
            </Button>
            <Button
              href={`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/dyslexia-demo`}
              target="_blank"
              variant="secondary"
              size="lg"
            >
              Dyslexia Demo
            </Button>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
