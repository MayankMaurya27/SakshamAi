import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { Menu, X } from "lucide-react";

import logo from "../../assets/logo/saksham-logo.png";

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItem =
    "text-slate-700 hover:text-[#1E3A5F] transition-colors font-medium";

  return (
    <nav className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-md">

      <div className="max-w-7xl mx-auto px-4 md:px-6">

        <div className="h-18 flex items-center justify-between">

          {/* Logo */}

          <Link
            to="/"
            className="flex items-center gap-2"
          >
            <img
              src={logo}
              alt="Saksham AI"
              className="h-10 w-10 object-contain"
            />

            <span className="font-bold text-2xl text-[#1E3A5F]">
              Saksham AI
            </span>
          </Link>

          {/* Desktop */}

          <div className="hidden lg:flex items-center gap-8">

            <NavLink to="/learn" className={navItem}>
              Learn
            </NavLink>

            <NavLink to="/quiz" className={navItem}>
              Quiz
            </NavLink>

            <NavLink to="/upload" className={navItem}>
              Notes
            </NavLink>

            <NavLink to="/accessibility" className={navItem}>
              Accessibility
            </NavLink>

            <NavLink to="/dashboard" className={navItem}>
              Dashboard
            </NavLink>

            <Link
              to="/learn"
              className="bg-[#1E3A5F] text-white px-5 py-2.5 rounded-xl font-semibold hover:scale-105 transition"
            >
              Ask AI
            </Link>

          </div>

          {/* Mobile Button */}

          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden"
          >
            {mobileOpen ? (
              <X size={28} />
            ) : (
              <Menu size={28} />
            )}
          </button>

        </div>

      </div>

      {/* Mobile Menu */}

      {mobileOpen && (
        <div className="lg:hidden border-t bg-white">

          <div className="flex flex-col px-4 py-4 gap-4">

            <NavLink
              to="/learn"
              onClick={() => setMobileOpen(false)}
            >
              Learn
            </NavLink>

            <NavLink
              to="/quiz"
              onClick={() => setMobileOpen(false)}
            >
              Quiz
            </NavLink>

            <NavLink
              to="/upload"
              onClick={() => setMobileOpen(false)}
            >
              Notes
            </NavLink>

            <NavLink
              to="/accessibility"
              onClick={() => setMobileOpen(false)}
            >
              Accessibility
            </NavLink>

            <NavLink
              to="/dashboard"
              onClick={() => setMobileOpen(false)}
            >
              Dashboard
            </NavLink>

            <Link
              to="/learn"
              onClick={() => setMobileOpen(false)}
              className="bg-[#1E3A5F] text-white text-center py-3 rounded-xl"
            >
              Ask AI
            </Link>

          </div>

        </div>
      )}
    </nav>
  );
}