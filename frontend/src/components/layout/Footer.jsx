import { Link } from "react-router-dom";
import {
  BookOpen,
  Brain,
  Accessibility,
  Globe,
  ArrowUpRight,
} from "lucide-react";

import logo from "../../assets/logo/saksham-logo.png";

export default function Footer() {
  return (
    <footer
      className="
        border-t
        border-slate-200
        bg-white/70
        backdrop-blur-md
        mt-20
      "
    >
      <div className="max-w-7xl mx-auto px-6 py-16">

        <div className="grid lg:grid-cols-4 gap-12">

          {/* Brand */}

          <div>
            <div className="flex items-center gap-3">

              <img
                src={logo}
                alt="Saksham AI"
                className="h-10 w-10 object-contain"
              />

              <div>
                <h3 className="font-bold text-xl text-[#1E3A5F]">
                  Saksham AI
                </h3>

                <p className="text-xs text-slate-500">
                  Learning Without Barriers
                </p>
              </div>

            </div>

            <p className="mt-5 text-slate-600 leading-relaxed">
              Curriculum-aware learning platform designed to make
              education more accessible, personalized, and effective
              for every student.
            </p>
          </div>

          {/* Platform */}

          <div>
            <h4 className="font-semibold text-[#1E3A5F] mb-5">
              Platform
            </h4>

            <div className="space-y-3 text-slate-600">

              <Link
                to="/learn"
                className="block hover:text-[#1E3A5F] transition-colors"
              >
                Learn
              </Link>

              <Link
                to="/quiz"
                className="block hover:text-[#1E3A5F] transition-colors"
              >
                Quiz
              </Link>

              <Link
                to="/upload"
                className="block hover:text-[#1E3A5F] transition-colors"
              >
                Notes
              </Link>

              <Link
                to="/dashboard"
                className="block hover:text-[#1E3A5F] transition-colors"
              >
                Dashboard
              </Link>

            </div>
          </div>

          {/* Features */}

          <div>
            <h4 className="font-semibold text-[#1E3A5F] mb-5">
              Core Features
            </h4>

            <div className="space-y-4">

              <div className="flex items-center gap-3 text-slate-600">
                <BookOpen size={18} />
                Curriculum Aware
              </div>

              <div className="flex items-center gap-3 text-slate-600">
                <Brain size={18} />
                Personalized Learning
              </div>

              <div className="flex items-center gap-3 text-slate-600">
                <Accessibility size={18} />
                Accessibility Support
              </div>

            </div>
          </div>

          {/* Project */}

          <div>
            <h4 className="font-semibold text-[#1E3A5F] mb-5">
              Project
            </h4>

            <div className="space-y-4">

              <a
                href="#"
                className="
                  flex
                  items-center
                  gap-2
                  text-slate-600
                  hover:text-[#1E3A5F]
                  transition-colors
                "
              >
                <Globe size={18} />
                Project Repository
              </a>

              <div className="flex items-center gap-2 text-slate-600">
                <ArrowUpRight size={18} />
                EDGE MINDS Challenge
              </div>

            </div>
          </div>

        </div>

        {/* Bottom */}

        <div
          className="
            mt-12
            pt-8
            border-t
            border-slate-200
            flex
            flex-col
            md:flex-row
            justify-between
            items-center
            gap-4
          "
        >

          <p className="text-slate-500 text-sm">
            © 2026 Saksham AI. All rights reserved.
          </p>

          <p className="text-slate-500 text-sm">
            Built for inclusive and accessible education.
          </p>

        </div>

      </div>
    </footer>
  );
}