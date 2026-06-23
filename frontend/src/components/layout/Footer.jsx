import { Link } from "react-router-dom";
import {
  BookOpen,
  Brain,
  Accessibility,
  Globe,
  ArrowUpRight,
  Heart,
} from "lucide-react";
import Logo from "../brand/Logo";

const platformLinks = [
  { to: "/learn", label: "Learn" },
  { to: "/quiz", label: "Quiz" },
  { to: "/upload", label: "Notes" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/accessibility", label: "Accessibility" },
];

const features = [
  { icon: BookOpen, label: "Curriculum Aware" },
  { icon: Brain, label: "Adaptive Learning" },
  { icon: Accessibility, label: "Inclusive Design" },
];

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-border glass-panel">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-12">
          <div className="sm:col-span-2 lg:col-span-1">
            <div className="flex items-center gap-3">
              <Logo size={40} />
              <div>
                <h3 className="font-bold text-lg text-primary">Saksham AI</h3>
                <p className="text-xs text-ink-muted font-medium">
                  Learning Without Barriers
                </p>
              </div>
            </div>
            <p className="mt-5 text-ink-muted text-sm leading-relaxed max-w-xs">
              An education platform that adapts to every learner — curriculum-aware,
              accessible, and built for classrooms that need more than chatbots.
            </p>
          </div>

          <div>
            <h4 className="font-bold text-ink text-sm mb-5">Platform</h4>
            <nav className="space-y-3">
              {platformLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className="block text-sm text-ink-muted hover:text-accent transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          <div>
            <h4 className="font-bold text-ink text-sm mb-5">Capabilities</h4>
            <div className="space-y-3">
              {features.map(({ icon: Icon, label }) => (
                <div
                  key={label}
                  className="flex items-center gap-2.5 text-sm text-ink-muted"
                >
                  <Icon size={16} className="text-accent shrink-0" />
                  {label}
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="font-bold text-ink text-sm mb-5">Project</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-ink-muted">
                <Globe size={16} className="text-neural shrink-0" />
                EDGE MINDS Challenge
              </div>
              <div className="flex items-center gap-2 text-sm text-ink-muted">
                <ArrowUpRight size={16} className="text-accent shrink-0" />
                Adaptive Learning Platform
              </div>
            </div>
          </div>
        </div>

        <div className="mt-14 pt-8 border-t border-border flex flex-col sm:flex-row justify-between items-center gap-4">
          <p className="text-ink-faint text-sm">
            © 2026 Saksham AI. All rights reserved.
          </p>
          <p className="text-ink-faint text-sm flex items-center gap-1.5">
            Built with <Heart size={14} className="text-primary" /> for inclusive education
          </p>
        </div>
      </div>
    </footer>
  );
}
